/**
 * Resolves the absolute URL for a Flamachat image based on its relative path.
 * Base URL: https://towebs.clientes.flamachat.com/
 * 
 * @param {string} path - The relative path from the database (e.g., "chats/IMAGE_....jpg" or "/chats/...")
 * @returns {string} - The full URL.
 */
export const getFlamachatUrl = (path) => {
    if (!path) return '';

    const baseUrl = "https://towebs.clientes.flamachat.com/file/";
    // Remove leading slash if present to avoid double slashes (though https://domain//path usually works, it's cleaner without)
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;

    return `${baseUrl}${cleanPath}`;
};
