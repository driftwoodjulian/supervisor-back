import json
from queue import Empty, Queue
from sqlite3.dbapi2 import Timestamp
import time
from flask import request
from datetime import datetime
import requests
# Assuming these services and imports are correct for your environment
from sockets.sock_extention import sock
from service.harmony_convertion import convert_to_harmony
from service.get_messages import get_messages
from service.get_chat import get_chat
from flask import current_app
from service.get_chat import get_current_chats
from controllers.satisfaction_controller import set_satisfaction
import random


import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define the base API endpoint URL (the port suffix will be added dynamically)
API_BASE_URL = "http://10.10.1.8:504{}"
API_BATCH_PATH = "/ai/ai/batch_score"
API_GPU_CHECK_PATH = "/ai/ai/check_gpu"
GPU_SERVER_COUNT = 3 # Number of GPU-enabled scoring services (e.g., 5040, 5041, 5042)
BATCH_SIZE = 2 # Desired batch size

scores = []
scores_lock = threading.Lock()
# Use a Queue to hold chat ID batches waiting to be processed
batch_queue = Queue()

processing_chats = set()
processing_lock = threading.Lock()
def is_score_present(message):
    # ... (existing logic remains the same)
    is_present = False

    if message["chat_id"] and len(scores)>0:
        i=0
        for score in scores:
            if score["chat_id"] and message["chat_id"]== score["chat_id"]:
                is_present=True
                print("updating chat id " + str(score["chat_id"]))
                scores[i] = message
                print(scores[i])
                break
            i+=1
    
    return is_present


def create_delay():
    return random.uniform(0.9, 0.5)

def gpu_available():
    """
    Checks ports 5040 to 504(GPU_SERVER_COUNT-1) for an available GPU.
    Returns the port suffix (0, 1, 2, ...) if available, or -1 if all are at capacity.
    """
    delay = create_delay()
    time.sleep(delay)
    for i in range(GPU_SERVER_COUNT):
        url = API_BASE_URL.format(str(i)) + API_GPU_CHECK_PATH
        try:
            # We use a short timeout since this is a quick status check
            response = requests.get(url)
            response.raise_for_status() # Raise exception for bad status codes
            
            # Assuming the response body is a JSON object like {"gpu": true/false}
            data = response.json()
            if data.get("gpu") == True:
                time.sleep(0.5)
                print(f"GPU available on port 504{i}")
                return i # Return the port suffix (0, 1, 2, ...)
                
        except requests.exceptions.RequestException as e:
            # Server is down, unreachable, or returned an error
            print(f"Error checking GPU on port 504{i}: {e}")
            continue
            
    print("All GPU servers currently at capacity or unreachable.")
    return -1 # Indicates no capacity


def eliminate_old_scores(chat_ids):
    global scores

    i = 0
    while i < len(scores) and len(scores)>0:
        try:
            score_id = scores[i]["chat_id"]
            is_found = False
            for chat_id in chat_ids:
                if chat_id == score_id:
                    is_found = True
                    break

            if not is_found:
                scores.pop(i)
            else:
                i += 1
        except Exception as e:
            # Corrected: print the exception object, not just 'e' as a string
            print(f"error eliminating old scores: {e}")


def batch_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# Initialize the GPU slot queue at the global level
# Initialize the GPU slot queue at the global level
gpu_slots = Queue()
for i in range(GPU_SERVER_COUNT):
    gpu_slots.put(i)

def batch_score_sender(app, batch_chat_ids):
    """
    1. Prepares data (I/O heavy).
    2. Claims a GPU slot from the queue (Blocking).
    3. Sends request and releases slot (Math heavy).
    """
    batch_prompts_data = []
    chat_id_map = {} 
    
    # STEP 1: Prepare data BEFORE claiming a GPU
    # We do this first so we don't hold a GPU slot while waiting for get_messages()
    with app.app_context():
        for i, chat_id in enumerate(batch_chat_ids):
            try:
                messages = get_messages(chat_id)
                chat = get_chat(chat_id)
                info = {
                    "conversation": messages["conversation"],
                    "chat_and_customer_info": chat
                }
                prompt_data = convert_to_harmony(full_chat=info) 
                batch_prompts_data.append(prompt_data)
                chat_id_map[i] = chat_id 
            except Exception as e:
                print(f"Error preparing chat_id {chat_id}: {e}")
                chat_id_map[i] = chat_id
                batch_prompts_data.append({})

    port_suffix = None
    try:
        # STEP 2: Claim a GPU slot
        # If all 3 are taken, this thread will pause here until one is put back.
        print(f"Batch {batch_chat_ids} waiting for an available GPU...")
        port_suffix = gpu_slots.get(block=True) 
        
        # STEP 3: Send the request
        api_endpoint_batch = API_BASE_URL.format(str(port_suffix)) + API_BATCH_PATH
        print(f"Sending batch {batch_chat_ids} to port 504{port_suffix}...")
        
        response = requests.post(
            api_endpoint_batch, 
            json=batch_prompts_data, 
             # Reduced timeout to something reasonable
        )
        response.raise_for_status()
        
        # Success! Map results back to chat_ids
        scores_list = response.json()
        final_results = {}
        for i, score_result in enumerate(scores_list):
            original_chat_id = chat_id_map.get(i)
            if original_chat_id:
                final_results[original_chat_id] = score_result
        return final_results

    except requests.exceptions.RequestException as e:
        print(f"Request error on port 504{port_suffix}: {e}")
        # If it was a 503, you might want to re-queue, but with this system 
        # 503s should be rare since we control the flow via gpu_slots.
        return {chat_id: {'error': f"API Error: {str(e)}"} for chat_id in batch_chat_ids}
        
    except Exception as e:
        print(f"Unexpected error in worker: {e}")
        return {chat_id: {'error': f"Internal Error: {str(e)}"} for chat_id in batch_chat_ids}

    finally:
        # STEP 4: Release the slot no matter what happens
        if port_suffix is not None:
            print(f"Releasing port 504{port_suffix}")
            gpu_slots.put(port_suffix)

"""
def batch_score_sender(app, batch_chat_ids):

    
    attempts = 0
    max_attempts = 1000 # Try to find a port/send 5 times before giving up
    
    # Pre-prepare data ONCE, not inside the loop
    batch_prompts_data = []
    chat_id_map = {} 
    
    with app.app_context():
        for i, chat_id in enumerate(batch_chat_ids):
            try:
                messages = get_messages(chat_id)
                chat = get_chat(chat_id)
                info = {
                    "conversation": messages["conversation"],
                    "chat_and_customer_info": chat
                }
                prompt_data = convert_to_harmony(full_chat=info) 
                batch_prompts_data.append(prompt_data)
                chat_id_map[i] = chat_id 
            except Exception as e:
                print(f"Error preparing chat_id {chat_id} for scoring: {e}")
                chat_id_map[i] = chat_id
                batch_prompts_data.append({})

    while attempts < max_attempts:
        # 1. Find a GPU
        port_suffix = gpu_available()
        
        if port_suffix == -1:
            print(f"No GPU available (Attempt {attempts+1}/{max_attempts}). Waiting...")
            time.sleep(1) # Wait a bit before checking again
            attempts += 1
            continue
        
        # 2. Construct endpoint
        api_endpoint_batch = API_BASE_URL.format(str(port_suffix)) + API_BATCH_PATH
        
        # 3. Send Request
        try:
            print(f"Sending batch of {len(batch_chat_ids)} chats to port 504{port_suffix}...")
            
            response = requests.post(
                api_endpoint_batch, 
                json=batch_prompts_data, 
                timeout=3000 
            )
            response.raise_for_status()
            
            # Success! Return results
            scores_list = response.json()
            final_results = {}
            for i, score_result in enumerate(scores_list):
                original_chat_id = chat_id_map.get(i)
                if original_chat_id:
                    final_results[original_chat_id] = score_result
            return final_results
            
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, 'status_code', None)
            if status_code == 503:
                print(f"Port 504{port_suffix} busy (503). Retrying different port...")
                # Do NOT increment attempts too fast, just loop to find another port
                # But to avoid infinite spinning if ALL are busy, we sleep/increment
                time.sleep(1)
                attempts += 1
                continue
            
            print(f"Error sending batch score request to port 504{port_suffix}: {e}")
            # Non-retryable error
            error_results = {chat_id: {'error': 'error with the score query'} for chat_id in batch_chat_ids}
            return error_results
            
    # If we exit loop, we failed to find a spot
    print(f"Failed to find GPU after {max_attempts} attempts. Re-queuing batch.")
    batch_queue.put(batch_chat_ids)
    return {chat_id: {'error': 'GPU capacity full (re-queued)'} for chat_id in batch_chat_ids}


# Set to track chat IDs that are currently in the queue or being processed
processing_chats = set()
processing_lock = threading.Lock()
"""
def query_scores(app):
    # Maximum workers now represents the number of concurrent GPU checks/batch senders.
    # Set to a value greater than GPU_SERVER_COUNT to allow checks to proceed faster.
    # Using 10 workers for a more aggressive parallel approach.
    executor = ThreadPoolExecutor(max_workers=10)
    cycle = 0

    while True:
        print(f"\n--- Start Cycle: {cycle} ---")
        
        try:
            # 1. Producer: Get all current chats
            chats = get_current_chats()
            all_chat_ids = [chat.id for chat in chats]

            if not all_chat_ids:
                with scores_lock:
                    scores.clear()
                    scores.append(json.dumps({"data": "No current chats"}))
                print("No current chats to score.")
            else:
                eliminate_old_scores(chat_ids=all_chat_ids)
                
                # Filter out chats that are already being processed
                chats_to_queue = []
                with processing_lock:
                    for cid in all_chat_ids:
                        if cid not in processing_chats:
                            chats_to_queue.append(cid)
                            processing_chats.add(cid) # Mark as in-progress
                
                if chats_to_queue:
                    new_batches = list(batch_list(chats_to_queue, BATCH_SIZE))
                    
                    # Add all new batches to the queue
                    for batch in new_batches:
                        if batch:
                            batch_queue.put(batch)
                    
                    print(f"Total current chats: {len(all_chat_ids)}. New items queued: {len(chats_to_queue)} ({len(new_batches)} batches)")
                else:
                    print(f"Total current chats: {len(all_chat_ids)}. No new items queued (all currently processing).")

            # 2. Consumer: Process items from the queue in parallel
            # We submit tasks for every item currently in the queue
            futures = {}
            while not batch_queue.empty():
                try:
                    batch = batch_queue.get_nowait()
                    time.sleep(create_delay())
                    # Submit ONE task (future) for the batch
                    future = executor.submit(batch_score_sender, app, batch)
                    futures[future] = batch
                except Empty:
                    break # Queue is empty
            
            if futures:
                print(f"Submitted {len(futures)} batch processing tasks to the executor.")
                
                for future in as_completed(futures):
                    batch_chat_ids = futures[future]
                    try:
                        # This result is a dictionary: {chat_id_1: score_1, ...}
                        batch_results = future.result()
                        
                        # Process individual results from the batch
                        for chat_id, score in batch_results.items():
                            
                            # Determine if we should clear the 'processing' flag
                            # We clear it if it's done (success) or a fatal error.
                            # We DO NOT clear it if it was re-queued (because it's still in the system)
                            
                            is_requeued = False
                            if "error" in score:
                                err_msg = str(score.get("error"))
                                if "re-queued" in err_msg:
                                    is_requeued = True
                                    print(f"Chat {chat_id} re-queued (busy). Remaining in processing set.")
                                else:
                                    print(f"Chat {chat_id} error: {err_msg}. Removing from processing set.")
                            else:
                                # Success case
                                message = {
                                    "chat_id": chat_id,
                                    "score": score,
                                    "timestamp": datetime.now().strftime("%H:%M:%S")
                                }

                                with scores_lock: # Apply lock for global list updates
                                    if not is_score_present(message):
                                        print(f"Appending new score: {message['chat_id']}")
                                        scores.append(message)
                                    else:
                                        print(f"Updated score of chat {chat_id}")
                            
                            # Cleanup processing set if finished (not re-queued)
                            if not is_requeued:
                                with processing_lock:
                                    if chat_id in processing_chats:
                                        processing_chats.remove(chat_id)
                                
                    except Exception as e:
                        print(f"Error processing result from batch {batch_chat_ids}: {e}")
                        # If a crash happens, safely release the processing locks for this batch
                        with processing_lock:
                            for cid in batch_chat_ids:
                                if cid in processing_chats:
                                    processing_chats.remove(cid)
            else:
                # print("No batches in queue to process.")
                pass


            # Sleep for the start of the next cycle
            time.sleep(3)
            cycle += 1
            
        except Exception as top_level_exc:
            print(f"Unexpected error in query_scores loop: {top_level_exc}")
            time.sleep(3)



'''
import json
from queue import Empty
from sqlite3.dbapi2 import Timestamp
import time
from flask import request
from datetime import datetime
import requests
from sockets.sock_extention import sock
from service.harmony_convertion import convert_to_harmony
from service.get_messages import get_messages
from service.get_chat import get_chat
from flask import current_app
from service.get_chat import get_current_chats
from controllers.satisfaction_controller import set_satisfaction


import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
api_endpoint_batch ="http://10.10.1.8:5040/ai/ai/batch_score"
scores = []
scores_lock = threading.Lock()

def is_score_present(message):
    
    is_present = False

    if message["chat_id"] and len(scores)>0:
        i=0
        for score in scores:
            if score["chat_id"] and message["chat_id"]== score["chat_id"]:
                is_present=True
                print("updating chat id " + str(score["chat_id"]))
                scores[i] = message
                print(scores[i])
                break
            i+=1
    
    return is_present

def gpu_available(): 

#here Im making a function that fetches http://10.10.1.8:504{port_variation}/ai/ai/check_gpu and on the app that returns true i will send the chat info so this function must return the iteration number that matches the port
# otherwise it will return -1 which will indicate at capacity for server
    portsuffix = None
    found= False
    i = 0
    #if you 3 ==
    while i<3 and found == False:
        portsuffix = requests.get(
            "http://10.10.1.8:504{}/ai/ai/check_gpu".format(str(i)),
        )

        response = portsuffix.json()
        if response["gpu"] == True:
            print("gpu available in port    " + str(i))
            found =True
            
        else:
            i+=1
            time.sleep(0.2)
    
    port = "504{}".format(str(i))

        
        



    


def eliminate_old_scores(chat_ids):
    global score

    i = 0
    while i < len(scores) and len(scores)>0:
        try:
            score_id = scores[i]["chat_id"]
            is_found = False
            for chat_id in chat_ids:
                if chat_id == score_id:
                    is_found = True
                    break

            if not is_found:
                scores.pop(i)
            else:
                i += 1
        except Exception as e:
            print("error eliminating old scores: " + e)


def batch_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def score_worker(app, chat_id):
    with app.app_context():
        return set_satisfaction(chat_id)



def batch_score_sender(app, batch_chat_ids):
    """
    Fetches all chat data for the batch and sends ONE SINGLE HTTP request 
    to the LLM service's batch endpoint for parallel GPU execution.
    """
    # 1. Aggregate the prompt data for the entire batch
    batch_prompts_data = []
    chat_id_map = {} 

    with app.app_context():
        for i, chat_id in enumerate(batch_chat_ids):
            # Existing data collection logic for one chat
            messages = get_messages(chat_id)
            chat = get_chat(chat_id)
            info = {
                "conversation": messages["conversation"],
                "chat_and_customer_info": chat
            }
            # The 'data' payload for the LLM service
            prompt_data = convert_to_harmony(full_chat=info) 
            
            batch_prompts_data.append(prompt_data)
            chat_id_map[i] = chat_id # Map request index to original chat_id

    # 2. Send the single batched request
    try:
        print(f"Sending batch of {len(batch_chat_ids)} chats to LLM service...")
        port = gpu_available()

        response = requests.post(
            api_endpoint_batch, # Use the new batch endpoint 
            json=batch_prompts_data, # <<< CRITICAL: Sending the list of prompts
             # Increased timeout
        )
        response.raise_for_status()
        
        # 3. Process the batched response (expects a LIST of score objects)
        scores_list = response.json()
        
        final_results = {}
        for i, score_result in enumerate(scores_list):
            original_chat_id = chat_id_map.get(i)
            if original_chat_id:
                final_results[original_chat_id] = score_result
        
        return final_results # Returns a dict: {chat_id: score_data, ...}
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending batch score request: {e}")
        # Return an error dict for every chat in the batch
        error_results = {chat_id: {'error': 'error with the score query'} for chat_id in batch_chat_ids}
        return error_results

def query_scores(app):
    # Executor max_workers now limits simultaneous BATCHES
    executor = ThreadPoolExecutor(max_workers=3)
    cycle = 0

    while True:
        print("cycle: " + str(cycle))
        try:
            chats = get_current_chats()
            chat_ids = [chat.id for chat in chats]

            if not chat_ids:
                # ... (Existing 'no current chats' logic)
                with scores_lock:
                    scores.clear()
                    scores.append(json.dumps({"data": "No current chats"}))
                
            else:
                eliminate_old_scores(chat_ids=chat_ids)

                for batch in batch_list(chat_ids, 2): # Use the intended batch size of 5

                    # 🛑 CRITICAL CHANGE: Submit ONE task for the entire batch
                    futures = {executor.submit(batch_score_sender, app, batch): batch} 
                    
                    for future in as_completed(futures):
                        # The result is a dictionary: {chat_id_1: score_1, ...}
                        try:
                            batch_results = future.result()
                            
                            # Process individual results from the batch
                            for chat_id, score in batch_results.items():
                                # NOTE: The retry logic is simplified since batch_score_sender handles the error:
                                # A full retry should use the original single set_satisfaction,
                                # but for this optimized setup, we will just log the error.


                                
                                

                                message = {
                                    "chat_id": chat_id,
                                    "score": score,
                                    "timestamp": datetime.now().strftime("%H:%M:%S")
                                }

                                with scores_lock: # Apply lock for global list updates
                                    if not is_score_present(message):
                                        print(f"appending new score: {message['chat_id']}")
                                        scores.append(message)
                                    else:
                                        # is_score_present already updates the score list for existing chats
                                        print(f"updated score of chat {chat_id}")
                                        
                        except Exception as e:
                            print(f"Error processing result from batch: {e}")

            time.sleep(3)
            cycle += 1
        except Exception as top_level_exc:
            print(f"unexpected error in query_scores loop: {top_level_exc}")
            time.sleep(3)
'''

'''
def query_scores(app):
    executor = ThreadPoolExecutor(max_workers=3)

    while True:
        try:
            chats = get_current_chats()
            chat_ids = [chat.id for chat in chats]

            if not chat_ids:
                with scores_lock:
                    scores.clear()
                    scores.append(json.dumps({"data": "No current chats"}))
            else:
                eliminate_old_scores(chat_ids=chat_ids)

                for batch in batch_list(chat_ids, 5):

                    # ★ FIXED: use score_worker instead of set_satisfaction
                    futures = {executor.submit(score_worker, app, chat_id): chat_id for chat_id in batch}

                    for future in as_completed(futures):
                        chat_id = futures[future]
                        try:
                            score = future.result()

                            retry_attempts = 0
                            while score == {'error': 'error with the score query'} and retry_attempts < 5:
                                print(f"error detected for chat {chat_id}, requerying (attempt {retry_attempts+1})")
                                score = score_worker(app, chat_id)
                                retry_attempts += 1

                            message = {
                                "chat_id": chat_id,
                                "score": score,
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            }

                            if not is_score_present(message):
                                with scores_lock:
                                    print(f"appending new score: {message['chat_id']}")
                                    scores.append(message)
                                    for s in scores:
                                        print(f"{s} --- in list")
                            else:
                                print(f"updated score of chat {chat_id}")

                        except Exception as e:
                            print(f"error fetching score for chat {chat_id}: {e}")

            time.sleep(3)

        except Exception as top_level_exc:
            print(f"unexpected error in query_scores loop: {top_level_exc}")
            time.sleep(3)


'''

'''
def query_scores():
    """
    Processes chat_ids in batches of 3. The global `scores` list grows cumulatively:
    after finishing each batch, new scored chat entries are appended (or existing ones updated).
    """
    # Reuse a single ThreadPoolExecutor across iterations to avoid re-creating threads too often.
    executor = ThreadPoolExecutor(max_workers=3)

    while True:
        try:
            chats = get_current_chats()
            chat_ids = [chat.id for chat in chats]

            if not chat_ids:
                with scores_lock:
                    scores.clear()
                    # Keep the same behavior you had before (a single JSON string entry)
                    scores.append(json.dumps({"data": "No current chats"}))
            else:
                # Remove scores that belong to chats that are no longer current
                eliminate_old_scores(chat_ids=chat_ids)

                # Process chat ids in batches of 3
                for batch in batch_list(chat_ids, 3):
                    # Submit the set_satisfaction calls for this batch
                    futures = {executor.submit(score_worker, chat_id): chat_id for chat_id in batch}

                    # As each future completes, append/update the global scores list
                    for future in as_completed(futures):
                        chat_id = futures[future]
                        try:
                            score = future.result()

                            # If the API sometimes returns an explicit error dict, retry here
                            # (mirrors your previous retry loop)
                            retry_attempts = 0
                            while score == {'error': 'error with the score query'} and retry_attempts < 5:
                                print(f"error detected for chat {chat_id}, requerying (attempt {retry_attempts+1})")
                                score = set_satisfaction(chat_id)
                                retry_attempts += 1

                            # Build message
                            message = {
                                "chat_id": chat_id,
                                "score": score,
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            }

                            # Append or update in a thread-safe way.
                            # IMPORTANT: we must append new items so the array grows cumulatively.
                            if not is_score_present(message):
                                with scores_lock:
                                    print(f"appending new score: {message['chat_id']}")
                                    scores.append(message)
                                    # print current list for debugging
                                    for s in scores:
                                        print(f"{s} --- in list")
                            else:
                                print(f"updated score of chat {chat_id}")

                        except Exception as e:
                            # keep the error message informative
                            print(f"error fetching score for chat {chat_id}: {e}")

            # small sleep before next full iteration
            time.sleep(3)
        except Exception as top_level_exc:
            # protect the loop from crashing
            print(f"unexpected error in query_scores loop: {top_level_exc}")
            time.sleep(3)
'''
'''
def query_scores():
    

    while True:
        chats = get_current_chats()
        chat_ids = [chat.id for chat in chats]
        
        if not chat_ids:
            scores.clear()
            scores.append(json.dumps({"data": "No current chats"}))
        else:
            #do a while loop that looks to match the id of the scores in the scores array and matches them with the ids in the chats_ids array, if no match is found in chats_ids then the score must be eliminated from the array
            eliminate_old_scores(chat_ids=chat_ids)



            for chat_id in chat_ids:
                try:
                    score_an_error= True
                    score= None
                    while score_an_error:
                        print()
                        score = set_satisfaction(chat_id) 
                        print("------------------")
                        print(str(score) + " ---- "+ str(chat_id) + " -----")
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        message = {
                            "chat_id": chat_id,
                            "score": score,
                            "timestamp": timestamp
                        }
                        print(message)
                        #chech if score it an error json here if not set score_not_an_error to True
                        if score =={'error': 'error with the score query'}:
                            print("error detected, requering")
                        else:
                            score_an_error= False 
                    try:
                        if not is_score_present(message=message):
                            print("appending new score: " + str(message["chat_id"]))

                            scores.append(message)
                            for scoree in scores:
                                print(str(scoree) +'--- in list')
                        else:
                            print("updated score of chat " + str(chat_id))
                    except:
                        print("error appending")   
                except Exception as e:
                    print(e)
                    print(f"error, we did get a score for chat {chat_id}: " + e)

        time.sleep(3)
'''


from decorators.auth import check_token_validity

@sock.route("/ws/satisfaction")
def satisfaction_ws(sock):
    """
    WebSocket endpoint for satisfaction scores.
    Requires 'token' query parameter for authentication.
    """
    token = request.args.get("token")
    if not token or not check_token_validity(token):
        sock.send(json.dumps({"error": "Unauthorized"}))
        sock.close()
        return

    while True:
        
        if len(scores) == 0:
            #sock.send(json.dumps({"chat_id": 0, "score": "neutral", "timestamp": "None"}))
            time.sleep(5)
        else:
            sock.send(json.dumps(scores))
            time.sleep(5)
        time.sleep(3)



