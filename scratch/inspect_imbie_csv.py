with open("data/raw/imbie/imbie3_antarctic_peninsula_Gt_partitioned.csv", "r", encoding="utf-8") as f:
    lines = [f.readline() for _ in range(50)]
for line in lines:
    print(line.strip())
