import axios, { AxiosResponse } from "axios";

/**
 * @param grammar 
 * @param route 
 */
export const postGrammar = (
  grammar: string,
  route: string = "/convert-dfa"
): Promise<AxiosResponse<any>> => {
  return axios.post(`http://localhost:8080${route}`, { grammar });
};
