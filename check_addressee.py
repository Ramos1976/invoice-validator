from validation.rules import check_addressee

test_names = ["Nir Aravot", "Teo Rantanen", "  nir aravot  ", None, ""]

for name in test_names:
    result = check_addressee(name)
    print(f"Input: {name!r:20} -> {result}")