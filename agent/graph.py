import pandas as pd

ANOMALY_PATH = "data/lakehouse/gold/anomalies_detected.parquet"
ROOT_CAUSE_PATH = "data/lakehouse/gold/anomaly_root_causes.parquet"


def load_data():
    anomalies = pd.read_parquet(ANOMALY_PATH)
    root_causes = pd.read_parquet(ROOT_CAUSE_PATH)

    # ✅ Normalize date types (CRITICAL)
    anomalies['usage_date'] = pd.to_datetime(anomalies['usage_date']).dt.date
    root_causes['usage_date'] = pd.to_datetime(root_causes['usage_date']).dt.date

    # Merge safely
    merged = anomalies.merge(
        root_causes,
        on=["usage_date", "service_name"],
        how="left"
    )

    return merged


def answer_question(question: str):
    df = load_data()

    question = question.lower()

    # Simple routing logic (can upgrade later)
    if "why" in question and "spike" in question:
        return explain_spikes(df)

    elif "which service" in question:
        return top_services(df)

    else:
        return "I can help with cost spikes and anomaly explanations."


def explain_spikes(df):
    if df.empty:
        return "No anomalies detected."

    latest = df.sort_values("usage_date", ascending=False).head(3)

    responses = []
    for _, row in latest.iterrows():
        responses.append(
    f"🔴 {row['service_name']} spike on {row['usage_date']}:\n"
    f"• Cause: {row.get('top_chip', 'unknown')} usage\n"
    f"• Region: {row.get('top_region', 'unknown')}\n"
    f"• Cost: ${row['service_cost']:.0f} ({row['deviation_ratio']:.1f}x baseline)"
)

    return "\n\n".join(responses)


def top_services(df):
    if df.empty:
        return "No anomalies found."

    counts = df['service_name'].value_counts().head(3)

    return "Top anomalous services:\n" + "\n".join(
        [f"{svc}: {cnt} spikes" for svc, cnt in counts.items()]
    )


if __name__ == "__main__":
    print("=== FinOps Intelligence Agent ===")

    while True:
        q = input("\nAsk a question (or 'exit'): ")

        if q.lower() == "exit":
            break

        answer = answer_question(q)
        print("\n🤖", answer)