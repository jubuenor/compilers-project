import axios from "axios";

export const postGrammar = (grammar: string) => {
    return axios.post("http://localhost:8080/convert", { grammar });
};
