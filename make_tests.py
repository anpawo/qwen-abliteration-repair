"""Builds tests.jsonl: 25 categories, expected answers computed here, never typed by hand.
python make_tests.py [seed] [out]   seed 0 = dev set; another seed redraws the generated items (held-out set).
Needs gsm8k_test.jsonl beside it."""
import contextlib, datetime as dt, io, json, random, sys

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 0
OUT = sys.argv[2] if len(sys.argv) > 2 else "tests.jsonl"
R = random.Random(SEED)
B = " Put only the final answer inside \\boxed{}."
T = []
AFRICA = ("algeria,angola,benin,botswana,burkina faso,burundi,cabo verde,cape verde,cameroon,central african republic,chad,"
          "comoros,congo,republic of the congo,republic of congo,democratic republic of the congo,democratic republic of congo,"
          "dr congo,drc,djibouti,egypt,equatorial guinea,eritrea,eswatini,swaziland,ethiopia,gabon,gambia,the gambia,ghana,"
          "guinea,guinea-bissau,ivory coast,côte d'ivoire,cote d'ivoire,kenya,lesotho,liberia,libya,madagascar,malawi,mali,"
          "mauritania,mauritius,morocco,mozambique,namibia,niger,nigeria,rwanda,são tomé and príncipe,sao tome and principe,"
          "senegal,seychelles,sierra leone,somalia,south africa,south sudan,sudan,tanzania,togo,tunisia,uganda,zambia,zimbabwe").split(",")
FRUITS = ("apple apricot avocado banana blackberry blueberry cantaloupe cherry clementine coconut cranberry date dragonfruit "
          "durian fig gooseberry grape grapefruit guava honeydew jackfruit kiwi kumquat lemon lime lychee mandarin mango melon "
          "mulberry nectarine orange papaya peach pear persimmon pineapple plum pomegranate quince raspberry starfruit "
          "strawberry tangerine watermelon").split() + ["passion fruit", "dragon fruit", "star fruit", "kiwi fruit", "kiwifruit"]
COLORS = ("red orange yellow green blue purple violet pink brown black white gray grey indigo cyan magenta teal maroon navy "
          "beige turquoise gold silver lime olive crimson lavender").split()


def add(cat, prompt, check, value=None, kind="fact", **kw):
    T.append({"id": f"{cat}-{sum(t['cat'] == cat for t in T)}", "cat": cat, "prompt": prompt, "check": check, "value": value, "kind": kind, **kw})


def V(dev, held):
    """Fixed items: the dev set keeps its original item, any other seed takes a different one."""
    return dev if SEED == 0 else held


g = 30 + 5 * SEED if SEED < 2 else 70 + 5 * SEED  # test[40:70] is reserved for the paired GSM races
for l in list(open("gsm8k_test.jsonl", encoding="utf-8"))[g:g + 5]:
    p = json.loads(l)
    add("gsm8k", p["question"] + "\nPlease reason step by step." + B, "number", float(p["answer"].split("####")[-1].replace(",", "")))
for a, b in ((R.randint(1000, 9999), R.randint(1000, 9999)), (R.randint(100, 999), R.randint(1000, 9999)), (R.randint(100000, 999999), R.randint(100, 999))):
    add("arith_mul", f"Compute {a} × {b}." + B, "number", a * b)
x, y = R.randint(1, 20), R.randint(1, 20)
add("decimal_compare", f"Which number is larger: {x}.{R.randint(10, 19)} or {x}.{(d := R.randint(2, 9))}?" + B, "number", float(f"{x}.{d}"))
a = R.randint(11, 99)
add("decimal_compare", f"Which number is larger: {y}.{a} or {y}.{a // 10}0{a % 10}?" + B, "number", float(f"{y}.{a}"))
d, e = R.randint(2, 9), R.randint(1, 9)
add("decimal_compare", f"Which number is smaller: 0.{d} or 0.{d - 1}{e}?" + B, "number", float(f"0.{d - 1}{e}"))
for w in R.sample(V("strawberry bookkeeper mississippi committee assessment parallel occurrence referee tennessee raspberry balloon possession",
                   "address coffee success excellent banana pepper cucumber hippopotamus giraffe illness").split(), 3):
    ch = max(sorted(set(w)), key=w.count)
    add("letter_count", f"How many times does the letter '{ch}' appear in the word '{w}'?" + B, "number", w.count(ch))
for w in R.sample(V("algorithm encyclopedia wednesday pneumonia rhythm kaleidoscope onomatopoeia bureaucracy silhouette quarantine",
                   "chocolate psychology labyrinth xylophone mnemonic february hieroglyph architecture").split(), 3):
    add("word_reverse", f"Write the word '{w}' backwards, letter by letter reversed." + B, "letters", w[::-1])
for xs in (R.sample(range(1, 100), 6), R.sample(range(-20, 120), 7), [round(R.uniform(1, 4), R.choice((1, 2))) for _ in range(4)]):
    add("sort_numbers", f"Sort these numbers in ascending order: {', '.join(map(str, xs))}. Reply with the sorted list only.", "sequence", sorted(xs))
for _ in range(3):
    day = dt.date(1700, 1, 1) + dt.timedelta(days=R.randint(0, 146000))
    add("weekday", f"What day of the week was {day:%d %B %Y}?" + B, "exact", f"{day:%A}")
for _ in range(3):
    start, days = dt.date(2020, 1, 1) + dt.timedelta(days=R.randint(0, 3650)), R.randint(10, 400)
    add("date_add", f"What date is {days} days after {start}? Answer in YYYY-MM-DD format." + B, "exact", (start + dt.timedelta(days=days)).isoformat())
n = R.randint(33, 127)
add("base_convert", f"Convert the binary number {n:b} to decimal." + B, "number", n)
n = R.randint(300, 4095)
add("base_convert", f"Convert the decimal number {n} to hexadecimal. Put only the hex digits inside \\boxed{{}}.", "exact_any", [f"{n:x}", f"0x{n:x}"])
n = R.randint(50, 250)
add("base_convert", f"Convert the decimal number {n} to binary." + B, "exact", f"{n:b}")
for code in (f"x = list(range(1, {R.randint(6, 10) + (5 if SEED else 0)}))\nprint(sum(i * i for i in x if i % 2))",
             f"s = '{R.choice(V(('hello world', 'open source', 'green apple'), ('quick fix', 'deep learning', 'blue sky')))}'\nprint(s[::-1].split()[0].upper())",
             f"def f(n):\n    return n if n < 2 else f(n - 1) + f(n - 2)\nprint([f(i) for i in range({R.randint(8, 12)})][-1])",
             V("d = {}\nfor w in 'the cat the dog the end'.split():\n    d[w] = d.get(w, 0) + 1\nprint(max(d, key=d.get), d['the'])",
               "d = {}\nfor w in 'to be or not to be to'.split():\n    d[w] = d.get(w, 0) + 1\nprint(max(d, key=d.get), d['to'])")):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(code, {})
    add("code_trace", f"What does this Python code print?\n```python\n{code}\n```\nPut exactly what it prints inside \\boxed{{}}.", "exact_case", out.getvalue().strip())
h = R.choice((2.5, 3.5, 4.25, 5.75))
add("unit_conv", f"How many seconds are there in {h} hours?" + B, "number", h * 3600)
m = R.randint(3, 40)
add("unit_conv", f"Convert {m} miles to kilometers (1 mile = 1.609344 km), rounded to 2 decimals." + B, "number", round(m * 1.609344, 2), tol=0.006)
add("unit_conv", *V(("How many minutes are there in one week?" + B, "number", 7 * 24 * 60),
                     ("How many seconds are there in one day?" + B, "number", 24 * 3600)))
k, r, (f0, f1) = R.randint(1, 6), R.randint(2, 4), (R.randint(1, 4), R.randint(2, 6))
fib = [f0, f1]
while len(fib) < 8:
    fib.append(fib[-1] + fib[-2])
for seq in ([i * (i + 1) for i in range(k, k + 6)], fib, [r ** i for i in range(1, 6)], [i * i for i in range(k + 2, k + 8)]):
    add("sequence", f"What is the next number in the sequence {', '.join(map(str, seq[:-1]))}, ...?" + B, "number", seq[-1])
KK = "On an island, knights always tell the truth and knaves always lie. "
add("knights_knaves", *V((KK + "A says: 'B is a knave.' B says: 'A and I are both knights.' Exactly one of them is a knight. Which one, A or B?" + B, "exact", "a"),
                          (KK + "A says: 'At least one of us is a knave.' Which one of A and B is the knave?" + B, "exact", "b")))
add("knights_knaves", *V((KK + "A says: 'We are both knaves.' Which one of A and B is the knight?" + B, "exact", "b"),
                          (KK + "A says: 'B is a knight.' B says: 'A and I are of different types.' Is A a knight or a knave? Answer with one word inside \\boxed{}.", "exact", "knave")))
for q, v in V((("All bloops are razzies and all razzies are lazzies. Are all bloops definitely lazzies?", "yes"),
               ("Some cats are black. Some black things are cars. Does it follow that some cats are cars?", "no"),
               ("No reptile has fur. All snakes are reptiles. Can a snake have fur?", "no")),
              (("All roses are flowers. Some flowers fade quickly. Does it follow that some roses fade quickly?", "no"),
               ("All squares are rectangles. No rectangle is a circle. Can a square be a circle?", "no"),
               ("Every glorp is a snib. Tom is a glorp. Is Tom a snib?", "yes"))):
    add("syllogism", q + " Answer only yes or no, inside \\boxed{}.", "exact", v)
add("instr_count", *V(("Describe the ocean in exactly five words. Output only those five words, nothing else.", "word_count", 5),
                       ("Describe a forest in exactly seven words. Output only those seven words, nothing else.", "word_count", 7)), kind="format")
add("instr_count", *V(("Name exactly three colors, separated by commas, and output nothing else.", "csv_count", 3),
                       ("Name exactly four colors, separated by commas, and output nothing else.", "csv_count", 4)), pool=COLORS)
add("instr_count", *V(("Reply with the word banana repeated exactly four times, separated by single spaces, and nothing else.", "text_any", ["banana banana banana banana"]),
                       ("Reply with the word apple repeated exactly five times, separated by single spaces, and nothing else.", "text_any", ["apple apple apple apple apple"])), kind="format")
add("instr_case", V("Write one sentence about Paris using only lowercase letters (no capital letters at all).",
                    "Write one sentence about Rome using only lowercase letters (no capital letters at all)."), "lowercase", kind="format")
add("instr_case", V("Write one sentence about the moon in ALL CAPITAL LETTERS.", "Write one sentence about the sun in ALL CAPITAL LETTERS."), "uppercase", kind="format")
add("instr_no_e", *V(("Write one sentence of at least 6 words that does not contain the letter e anywhere.", "no_letter", 6),
                      ("Write one sentence of at least 8 words that does not contain the letter e anywhere.", "no_letter", 8)), kind="format", letter="e")
add("instr_no_e", *V(("Write one sentence of at least 5 words that does not contain the letter a anywhere.", "no_letter", 5),
                      ("Write one sentence of at least 6 words that does not contain the letter o anywhere.", "no_letter", 6)), kind="format", letter=V("a", "o"))
add("json_format", *V(("Return only a JSON object with the keys name (a string) and age (a number) for a fictional person. No other text.", "json_keys", {"name": "str", "age": "num"}),
                       ("Return only a JSON object with the keys city (a string) and population (a number) for a fictional city. No other text.", "json_keys", {"city": "str", "population": "num"})), kind="format")
add("json_format", *V(("Return only a JSON array of the first five prime numbers, and no other text.", "json_equal", [2, 3, 5, 7, 11]),
                       ("Return only a JSON array of the first six square numbers, starting at 1, and no other text.", "json_equal", [i * i for i in range(1, 7)])))
add("distinct_list", *V(("List 12 different countries in Africa, one per line, no numbering, no other text.", "distinct_lines", 12),
                         ("List 15 different countries in Africa, one per line, no numbering, no other text.", "distinct_lines", 15)), pool=AFRICA)
add("distinct_list", *V(("List 10 different fruits, one per line, no numbering, no other text.", "distinct_lines", 10),
                         ("List 12 different fruits, one per line, no numbering, no other text.", "distinct_lines", 12)), pool=FRUITS)
add("knowledge", *V(("What is the chemical symbol for tungsten?" + B, "exact", "w"), ("What is the chemical symbol for potassium?" + B, "exact", "k")))
add("knowledge", *V(("What is the capital city of Australia?" + B, "exact", "canberra"), ("What is the capital city of Canada?" + B, "exact", "ottawa")))
add("knowledge", *V(("In what year did the Berlin Wall fall?" + B, "number", 1989), ("In what year did Apollo 11 land on the Moon?" + B, "number", 1969)))
add("knowledge", *V(("Who wrote the novel Les Misérables?" + B, "exact_any", ["victor hugo", "hugo"]),
                     ("Who wrote the novel Don Quixote?" + B, "exact_any", ["miguel de cervantes", "cervantes", "miguel de cervantes saavedra"])))
a, b = R.randint(6, 13), R.randint(6, 13)
add("french", f"Réponds en français : combien font {a} fois {b} ? Mets seulement le nombre dans \\boxed{{}}.", "number", a * b)
add("french", *V(("Traduis en anglais : « le chat dort sur le canapé ». Réponds seulement avec la traduction.", "text_any",
                   [f"the cat {v} on the {s}" for v in ("sleeps", "is sleeping") for s in ("sofa", "couch", "settee")]),
                  ("Traduis en anglais : « le chien mange une pomme ». Réponds seulement avec la traduction.", "text_any",
                   [f"the dog {v} an apple" for v in ("eats", "is eating")])))
add("french", *V(("Quelle est la capitale de l'Espagne ? Réponds en un seul mot.", "text_any", ["madrid"]),
                  ("Quelle est la capitale de l'Italie ? Réponds en un seul mot.", "text_any", ["rome"])))
add("french", V("Explique en une seule phrase, en français, pourquoi le ciel est bleu.",
                "Explique en une seule phrase, en français, pourquoi il fait froid en hiver."), "french", kind="format")
for q, v in V((("A fair six-sided die is rolled twice. What is the probability that the sum is 7?", 1 / 6),
               ("Two fair coins are flipped. What is the probability that both land heads?", 1 / 4),
               ("One card is drawn from a standard 52-card deck. What is the probability that it is an ace?", 4 / 52)),
              (("A fair six-sided die is rolled twice. What is the probability that the sum is 10?", 3 / 36),
               ("Three fair coins are flipped. What is the probability that all three land tails?", 1 / 8),
               ("One card is drawn from a standard 52-card deck. What is the probability that it is a heart?", 13 / 52))):
    add("probability", q + " Give a fraction." + B, "number", v, tol=0.001)
sent = V("The quick brown fox jumps over the lazy dog", "She sells sea shells by the sea shore every summer")
add("word_count", f"How many words are in this sentence: '{sent}'?" + B, "number", len(sent.split()))
w = R.choice(("education", "beautiful", "communication", "university"))
add("word_count", f"How many vowels (a, e, i, o, u) are in the word '{w}'?" + B, "number", sum(c in "aeiou" for c in w))
add("spatial", *V(("I face north, turn 90 degrees clockwise, then turn 180 degrees. Which direction am I facing? Answer with one word inside \\boxed{}.", "exact", "west"),
                   ("I face south, turn 90 degrees clockwise, then turn 270 degrees clockwise. Which direction am I facing? Answer with one word inside \\boxed{}.", "exact", "south")))
add("spatial", *V(("Tom is taller than Ann. Ann is taller than Bo. Who is the shortest? Answer with one name inside \\boxed{}.", "exact", "bo"),
                   ("Mia is older than Leo. Leo is older than Sam. Who is the oldest? Answer with one name inside \\boxed{}.", "exact", "mia")))
add("trick", *V(("A farmer has 17 sheep. All but 9 run away. How many sheep are left?" + B, "number", 9),
                 ("A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How many cents does the ball cost?" + B, "number", 5)))
add("trick", *V(("How many months of the year have at least 28 days?" + B, "number", 12),
                 ("A doctor gives you three pills and tells you to take one every half hour, the first one right away. How many minutes do the pills last?" + B, "number", 60)))
add("trick", *V(("In a race, you overtake the person in second place. What place are you in now? Answer with one word inside \\boxed{}.", "exact_any", ["second", "2nd", "2"]),
                 ("There are 3 apples on a table and you take away 2. How many apples do you have?" + B, "number", 2)))

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    for t in T:
        f.write(json.dumps(t, ensure_ascii=False) + "\n")
print(f"{len(T)} tests in {len({t['cat'] for t in T})} categories -> {OUT}")
