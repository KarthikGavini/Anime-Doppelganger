// frontend/src/hooks/useWebcam.ts
import { useState, useRef, useCallback, useEffect } from 'react';

export const useWebcam = () => {
  const [isWebcamOpen, setIsWebcamOpen] = useState(false);
  const [webcamError, setWebcamError] = useState<string | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);

  const openWebcam = useCallback(async () => {
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error("Webcam API not available in this browser.");
      }
      const newStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(newStream);
      setIsWebcamOpen(true);
      setWebcamError(null);
    } catch (err) {
      setWebcamError("Could not access webcam. Please check permissions.");
      console.error("Webcam Error:", err);
    }
  }, []);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
      videoRef.current
        .play()
        .catch(err => console.error("Video play error:", err));
    }
  }, [stream]);

  const closeWebcam = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    setStream(null);
    setIsWebcamOpen(false);
  }, [stream]);

  const takePicture = useCallback((): Promise<File | null> => {
    return new Promise((resolve) => {
      if (videoRef.current && videoRef.current.videoWidth > 0 && videoRef.current.videoHeight > 0) {
        const canvas = document.createElement('canvas');
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;

        const context = canvas.getContext('2d');
        if (context) {
          context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
          canvas.toBlob(blob => {
            if (blob) {
              resolve(new File([blob], "webcam-photo.jpg", { type: "image/jpeg" }));
            } else {
              resolve(null);
            }
          }, 'image/jpeg');
        } else {
          resolve(null);
        }
      } else {
        console.warn("Video not ready yet.");
        resolve(null);
      }
    });
  }, []);

  return { isWebcamOpen, webcamError, videoRef, openWebcam, closeWebcam, takePicture };
};
