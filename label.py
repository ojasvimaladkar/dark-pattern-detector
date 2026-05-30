import pandas as pd

df = pd.read_csv("data/raw_scraped.csv")

unlabelled = df[df['is_dark_pattern'] == 0].sample(100, random_state=42)

labels = []
for i, row in unlabelled.iterrows():
    print(f"\n[{len(labels)+1}/100]")
    print(f"TEXT: {row['text']}")
    label = input("Dark pattern? 1=yes, 0=no, s=skip: ").strip()
    if label == 's':
        continue
    labels.append({"text": row["text"], "manual_label": int(label)})

manual_df = pd.DataFrame(labels)
manual_df.to_csv("data/manual_labels.csv", index=False)
print(f"\nSaved {len(manual_df)} manual labels.")