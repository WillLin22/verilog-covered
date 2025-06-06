with open("./testdata/f32_add.io15M", "r") as f:
    ios = f.readlines()
    exist = set()
    with open("./testdata/f32_add.io15M.modified", "w+") as fout:
        for io in ios:
            if io not in exist:
                exist.add(io)
                fout.write(io)
