import { TOKEN_STORAGE_KEY } from "./auth";

export class UnauthorizedError extends Error {
    constructor(message = "Unauthorized") {
        super(message);
        this.name = "UnauthorizedError";
    }
}

export const authenticatedFetch = async (url, options = {}) => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);

    const headers = {
        ...options.headers,
        "Authorization": `Bearer ${token}`
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        throw new UnauthorizedError();
    }

    return response;
};
