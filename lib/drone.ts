import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_VERCEL_URL
  ? `https://${process.env.NEXT_PUBLIC_VERCEL_URL}/api`
  : "http://localhost:3000/api";

export const takeoff = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/takeoff`);
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
    const response = await axios.post(`${API_BASE_URL}/land`);
    return response.data;
  } catch (error) {
    console.error("Error landing:", error);
    throw error;
  }
};

export const getVideoFeedUrl = () => {
  return `${API_BASE_URL}/video_feed`;
};
