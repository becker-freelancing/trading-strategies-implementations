def convert(path):
    write_path = path + ".textable"
    with open(path, "r") as file:
        with open(write_path, "w") as writ_file:
            lines = file.readlines()
            for line in lines:
                split = line.split(",")
                if len(split[0]) != 0:
                    split[0] = "\\textbf{" + split[0] + "}"
                for i in range(1, len(split)):
                    try:
                        split[i] = str(round(float(split[i]), 2))
                    except Exception:
                        pass
                join = " & ".join(split) + " \\\\\n"
                writ_file.write(join)


if __name__ == "__main__":
    for p in ["./analysis.csv", "./backtest.csv", "./test.csv", "./train.csv", "./validation.csv"]:
        convert(p)
