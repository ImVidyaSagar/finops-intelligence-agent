import pandas as pd

DETECTED_PATH = "data/lakehouse/gold/anomalies_detected.parquet"
GROUND_TRUTH_PATH = "data/mock/anomalies_ground_truth.csv"

def evaluate():
    print("=== Anomaly Detection Accuracy ===")

    detected = pd.read_parquet(DETECTED_PATH)
    truth = pd.read_csv(GROUND_TRUTH_PATH)

    # Normalize columns
    detected['usage_date'] = pd.to_datetime(detected['usage_date'])
    truth['date'] = pd.to_datetime(truth['date'])

    # Match keys
    detected['key'] = detected['usage_date'].astype(str) + "_" + detected['service_name']
    truth['key'] = truth['date'].astype(str) + "_" + truth['service_name']

    detected_set = set(detected['key'])
    truth_set = set(truth['key'])

    # Metrics
    true_positives = len(detected_set & truth_set)
    false_positives = len(detected_set - truth_set)
    false_negatives = len(truth_set - detected_set)

    precision = true_positives / len(detected_set) if detected_set else 0
    recall = true_positives / len(truth_set) if truth_set else 0

    print(f"Detected:        {len(detected_set)}")
    print(f"Actual:          {len(truth_set)}")
    print(f"True Positives:  {true_positives}")
    print(f"False Positives: {false_positives}")
    print(f"Missed:          {false_negatives}")

    print("\n📊 Metrics:")
    print(f"Precision: {precision:.2f}")
    print(f"Recall:    {recall:.2f}")


if __name__ == "__main__":
    evaluate()