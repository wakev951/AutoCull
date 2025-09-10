# photo_scorer.py
import cv2
import numpy as np
from skimage import filters
from db import Database

class PhotoScorer:
    """
    Comprehensive image scoring using OpenCV and skimage.
    Stores all computed metrics in the database if a DB instance is provided.
    """
    def __init__(self, db: Database = None):
        self.db = db

    def score_photo(self, file_path):
        """
        Compute a variety of metrics for the image.
        Returns a dictionary of metric_name -> value.
        """
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError(f"Cannot read image: {file_path}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        scores = {
            # ---------------- Sharpness / focus ----------------
            "laplacian_var": float(cv2.Laplacian(gray, cv2.CV_64F).var()),
            "sobel_energy": float(np.sum(np.square(cv2.Sobel(gray, cv2.CV_64F,1,0))) +
                                  np.sum(np.square(cv2.Sobel(gray, cv2.CV_64F,0,1)))),

            # ---------------- Noise ----------------
            "noise": float(np.mean(np.abs(gray - cv2.GaussianBlur(gray,(3,3),0)))),

            # ---------------- Exposure / brightness ----------------
            "brightness_mean": float(np.mean(gray)),
            "brightness_median": float(np.median(gray)),
            "saturation_mean": float(np.mean(hsv[:,:,1])),
            "saturation_std": float(np.std(hsv[:,:,1])),

            # ---------------- Contrast ----------------
            "contrast_std": float(np.std(gray)),
            "contrast_range": float(gray.max() - gray.min()),

            # ---------------- Colorfulness ----------------
            "colorfulness": self._colorfulness(img),

            # ---------------- Entropy / texture ----------------
            "entropy": float(self._entropy(gray)),

            # ---------------- Size / aspect ----------------
            "width": img.shape[1],
            "height": img.shape[0],
            "aspect_ratio": img.shape[1] / img.shape[0],
        }

        return scores

    def score_and_store(self, photo_id, file_path):
        """
        Compute all metrics and store them in the DB for the given photo_id.
        """
        if self.db is None:
            raise ValueError("Database instance not provided.")
        scores = self.score_photo(file_path)

        # Save all metrics
        for metric_name, value in scores.items():
            self.db.add_score(photo_id, metric_name, float(value))

        return scores

    # ---------------- Metric helpers ----------------
    def _colorfulness(self, img):
        """
        Measures colorfulness using the Hasler & Süsstrunk method.
        """
        (B, G, R) = cv2.split(img.astype("float"))
        rg = np.abs(R - G)
        yb = np.abs(0.5 * (R + G) - B)
        return float(np.sqrt(rg.mean()**2 + yb.mean()**2) + 0.3 * (rg.std() + yb.std()))

    def _entropy(self, gray):
        """
        Computes Shannon entropy of a grayscale image.
        """
        hist = cv2.calcHist([gray], [0], None, [256], [0,256])
        hist_norm = hist.ravel() / hist.sum()
        hist_norm = hist_norm[hist_norm > 0]
        return float(-np.sum(hist_norm * np.log2(hist_norm)))
