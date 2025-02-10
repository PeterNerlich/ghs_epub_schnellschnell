#!/usr/bin/env python3

import sys
import re
from typing import TYPE_CHECKING
from typing import Iterable
from functools import reduce
from pprint import pprint, pformat

if TYPE_CHECKING:
	pass


targets = {
	"c11": range(1, 32+1),
	"c12": range(33, 66+1),
	"c13": range(67, 93+1),

	"c15": range(94, 104+1),
	"c16": range(105, 119+1),
	"c17": range(120, 129+1),
	"c18": range(130, 144+1),
	"c19": range(145, 164+1),
	"c20": range(165, 175+1),
	"c21": range(176, 185+1),
	"c22": range(186, 203+1),
	"c23": range(204, 224+1),

	"c25": range(225, 236+1),
	"c26": range(237, 260+1),
	"c27": range(261, 276+1),
	"c28": range(277, 291+1),
	"c29": range(292, 296+1),
	"c30": range(297, 309+1),
	"c31": range(310, 323+1),

	"c33": range(324, 332+1),
	"c34": range(333, 345+1),
	"c35": range(346, 355+1),
	"c36": range(356, 371+1),
	"c37": range(372, 381+1),
	"c38": range(382, 393+1),

	"c40": range(394, 412+1),
	"c41": range(413, 438+1),
	"c42": range(439, 462+1),
	"c43": range(463, 475+1),
	"c44": range(476, 491+1),
	"c45": range(492, 505+1),
	"c46": range(506, 517+1),
	"c47": range(518, 521+1),
	"c48": range(522, 544+1),

	"c50": ["545a", "545b", *range(546, 560+1)],
	"c51": range(561, 577+1),
	"c52": range(578, 585+1),
	"c53": range(586, 591+1),
	"c54": range(592, 607+1),
	"c55": range(608, 620+1),
	"c56": range(621, 630+1),
	"c57": range(631, 640+1),

	"c59": range(641, 646+1),
	"c60": range(647, 656+1),
	"c61": range(657, 661+1),
	"c62": range(662, 668+1),
	"c63": range(669, 679+1),
	"c64": range(680, 694+1),
}

nums = [
    (num, target)
    for target, nums in targets.items()
    for num in nums
]
target_lookup = {
    str(num): target
    for target, nums in targets.items()
    for num in nums
}


ordinals = {
	1: "Erste",
	2: "Zweite",
	3: "Dritte",
	4: "Vierte",
	5: "Fünfte",
	6: "Sechste",
	7: "Siebente",
	8: "Achte",
	9: "Neunte",
}


filename = "schnellschnell"

preamble = """
<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>glauben hoffen singen</title>
  <link href="../Styles/epub.css" rel="stylesheet" type="text/css" />
  <meta content="width=0, height=0" name="viewport" />
</head>

<body>
  <div class="anchors" style="display: none;">
    <a id="{filename}"></a>
  </div>
""".lstrip("\n")

page_preamble = """
  <div id="d{prefix}" style="min-height: 100vh;">

    <h2></h2>

    <h1><strong>Schnell-Schnellmenü</strong></h1>

    <div style="display: flex; justify-content: space-between;">
      <a class="tRef" href="../Text/{root}.html#d{root}">Löschen und neue Nummer aufschlagen</a>
      <a class="tRef" href="../Text/{prev_file}.html#d{prev_prefix}">Letzte Ziffer löschen</a>
    </div>

    <h1>{prefix}…</h1>
""".lstrip("\n")

next_preamble = """
    <p class="oe_gross"><strong>{nth} Ziffer:</strong></p>

    <div class="table">
      <table>
        <tr>
""".lstrip("\n")

next_entry = """
          <td>
            <p class="ctr oe_gross"><a class="tRef" href="../Text/{index}.html#d{prefix}{digit}">&nbsp;&nbsp;{digit}&nbsp;&nbsp;</a></p>
          </td>
""".lstrip("\n")

next_rowsep = """
        </tr>

        <tr>
""".lstrip("\n")

next_epilog = """
        </tr>
      </table>
    </div>
""".lstrip("\n")

direct_preamble = """
    <p><strong>Direkt aufschlagen:</strong></p>

    <div class="table">
      <table>
        <tr>
""".lstrip("\n")

direct_entry = """
          <td>
            <p class="ctr"><a class="sRef" href="../Text/{chapter}.html#s{num}">&nbsp;{num}&nbsp;</a></p>
          </td>
""".lstrip("\n")

direct_highlight = """
          <td>
            <p class="ctr oe_gross"><strong><a class="sRef" href="../Text/{chapter}.html#s{num}">&nbsp;{num}&nbsp;</a></strong></p>
          </td>
""".lstrip("\n")

direct_rowsep = """
        </tr>

        <tr>
""".lstrip("\n")

direct_epilog = """
        </tr>
      </table>
    </div>
""".lstrip("\n")

page_epilog = """
  </div>
  <span style="page-break-after: always" />
""".lstrip("\n")

epilog = """
</body>
</html>
""".lstrip("\n")


def get_digit_tree(remaining: Iterable[tuple[str, str]] = []) -> dict[str, dict]:
	return {
		"prefix": "",
		"digits": _get_digit_tree_recurse(remaining, ""),
		"direct": [],
	}

def _get_digit_tree_recurse(remaining: Iterable[tuple[str, str]], prefix: str) -> dict[str, dict]:
	def add(acc: dict[str, Iterable[str]], x: tuple[str, str]) -> dict[str, Iterable[str]]:
		rest, full = x
		if rest:
			if rest[0] not in acc:
				acc[rest[0]] = []
			acc[rest[0]].append((rest[1:], full))
		return acc

	buckets = reduce(add, remaining, {})

	def comparable_number(x: str):
		try:
			return int(x) % 10
		except ValueError:
			match = re.match(r'(\d+)', x)
			return int(match.group()) % 10 if match else 10

	return {
		digit[0]: {
			"prefix": f"{prefix}{digit[0]}",
			"digits": _get_digit_tree_recurse(rest, f"{prefix}{digit[0]}"),
			"direct": [
				row
				for sublist in [
					[num for r, num in rest if len(r) == rest_length]
					for rest_length in [0, 1]
				]
				for row in (
					[num for num in sublist if comparable_number(num) < 5],
					[num for num in sublist if comparable_number(num) >= 5]
				)
				if row
			],
		}
		for digit, rest in buckets.items()
	}


def generate(targets: dict[Iterable[tuple[str|int]]]) -> str:
	all_nums = [str(num) for num, target in nums]
	print(f"Generating quick access menu for {len(all_nums)} targets…")
	digit_tree = get_digit_tree([(num, num) for num in all_nums])

	docs = flatten_tree_to_files_with_pages(digit_tree)

	total_pages = reduce(lambda acc, pages: acc+len(pages), docs.values(), 0)
	print(f"Typesetting {total_pages} pages in {len(list(docs.keys()))} docs…")
	for doc, pages in docs.items():
		if doc == "root":
			name = f"{filename}"
		else:
			name = f"{filename}{doc}"

		with open(f"{name}.html", "w") as file:
			print(f"generating {name}…")
			file.write(write_pages(pages, name, root=filename))
	print("Done!")


def write_pages(pages, filename, root) -> str:
	out = ""

	out += preamble.format(filename=filename)
	for page in pages:
		out += page_preamble.format(prefix=page["prefix"], root=root, prev_file=filename[:-1] if len(page["prefix"]) <= 2 and page["prefix"] != "" else filename, prev_prefix=page["prefix"][:-1])

		if "digits" in page and page["digits"]:
			nth = len(page["prefix"]) + 1
			groupings = [
				[None, None, 0, None, None],
				[None, 1, 2, 3, None],
				[None, 4, 5, 6, None],
				[None, 7, 8, 9, None],
			]

			if any(str(digit) in page["digits"] for row in groupings for digit in row if digit is not None):
				out += next_preamble.format(prefix=page["prefix"], nth=ordinals[nth] if nth in ordinals else f"{nth}.")
				out += next_rowsep.join([
					"".join([
						next_entry.format(
							filename=filename,
							index=f'{filename}{digit}' if len(page["prefix"]) <= 1 and digit is not None and str(digit) in page["digits"] else filename,
							prefix=page["prefix"],
							digit=str(digit) if str(digit) in page["digits"] else ""
						)
						for digit in row
					])
					for row in groupings
				])
				out += next_epilog
		
		if "direct" in page and page["direct"]:
			out += direct_preamble
			out += direct_rowsep.join([
				"".join([
					(direct_highlight if num == page["prefix"] else direct_entry).format(filename=filename, num=num, chapter=target_lookup[num])
					for num in row
				])
				for row in page["direct"]
			])
			out += direct_epilog

		out += page_epilog
	out += epilog
	
	return out


def flatten_tree_to_files_with_pages(tree: dict[str, str | Iterable[dict[str, str]]]) -> Iterable[dict[str, str | Iterable[str]]]:
	return {
		"root": [
			{
				"prefix": tree["prefix"],
				"digits": list(tree["digits"].keys()),
				"direct": tree["direct"],
			},
		],
		**{
			digit: [
				{
					"prefix": items["prefix"],
					"digits": list(items["digits"].keys()),
					"direct": items["direct"],
				}
			]
			for digit, items in tree["digits"].items()
			if items["digits"] or items["direct"]
		},
		**{
			f'{digit}{subdigit}': _flatten_trees_to_pages([items])
			for digit, subitems in [
				(digit, items["digits"])
				for digit, items in tree["digits"].items()
				if "digits" in items and items["digits"]
			]
			for subdigit, items in subitems.items()
			if items["digits"] or items["direct"]
		},
	}

def _flatten_trees_to_pages(trees: Iterable[dict]) -> Iterable[dict[str, str | Iterable[str]]]:
	if not trees:
		return []
	return [
		*[
			{
				"prefix": tree["prefix"],
				"digits": list(tree["digits"].keys()),
				"direct": tree["direct"],
			}
			for tree in trees
		],
		*_flatten_trees_to_pages([
			items
			for tree in trees
			for digit, items in tree["digits"].items()
			if items["digits"] or items["direct"]
			#if items["digits"]
		])
	]


if __name__ == '__main__':
	generate(targets)
