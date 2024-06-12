import axios from "axios";

const API_BASE_URL = "http://localhost:3000/api";

export const takeoff = async () => {
  try {
    const response = await axios.post(`http://127.0.0.1:5328/takeoff`);
    return response.data;
  } catch (error) {
    console.error("Error taking off:", error);
    throw error;
  }
};

export const health = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/healthchecker`);
    return response.data;
  } catch (error) {
    console.error("Error connecting:", error);
    throw error;
  }
};

export const land = async () => {
  try {
    const response = await axios.post(`http://localhost:5328/land`);
    return response.data;
  } catch (error) {
    console.error("Error landing:", error);
    throw error;
  }
};

export const getVideoFeedUrl = () => {
  return `${API_BASE_URL}/video_feed`;
};
