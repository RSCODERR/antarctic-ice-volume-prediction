with open("antarctic-ice-volume-prediction/data/raw/userguide_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Print pages 2, 3, 4 where parameters are described
start_p2 = text.find("--- PAGE 2 ---")
end_p5 = text.find("--- PAGE 6 ---")
if start_p2 != -1 and end_p5 != -1:
    print(text[start_p2:end_p5])
else:
    print(text[:4000])

