// this is a quick and dirty JS port of generate_quickmenu.py

function range(start, end) {
  return Array.from({ length: end-start }, (_, i) => i + start);
}

const targets = {
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

  "c50": ["545a", "545b"].concat(range(546, 560+1)),
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
  "c64": range(680, 694+1)
};

const nums = Object.entries(targets)
  .flatMap(([target, nums]) => nums.map(num => [num, target]));
const targetLookup = Object.fromEntries(Object
  .entries(targets)
  .flatMap(([target, nums]) => nums.map(num => [String(num), target])));


const ordinals = {
  1: "Erste",
  2: "Zweite",
  3: "Dritte",
  4: "Vierte",
  5: "Fünfte",
  6: "Sechste",
  7: "Siebente",
  8: "Achte",
  9: "Neunte",
};

const filename = "schnellschnell";


function getDigitTree(remaining = []) {
  return {
    prefix: "",
    digits: _getDigitTreeRecurse(remaining, ""),
    direct: [],
  };
}

function _getDigitTreeRecurse(remaining, prefix) {
  const buckets = remaining.reduce((acc, x) => {
    const [rest, full] = x;
    if (rest) {
      if (!acc[rest[0]]) {
        acc[rest[0]] = [];
      }
      acc[rest[0]].push([rest.slice(1), full]);
    }
    return acc;
  }, {});

  function comparableNumber(x) {
    let num = parseInt(x) % 10;
    if (isNaN(num)) {
      match = x.match(/^\d+/);
      num = match ? parseInt(match[0]) % 10 : 10;
    }
    return num;
  }




  const tree = {};
  Object.entries(buckets).forEach(([digit, rest]) => {
    tree[digit[0]] = {
      prefix: prefix + digit[0],
      digits: _getDigitTreeRecurse(rest, prefix + digit[0]),
      direct: [0, 1]
        .map(restLength => rest
          .filter(([r, num]) => r.length === restLength)
          .map(([r, num]) => num))
        .reduce((acc, sublist) => {
          const under = sublist.filter(num => comparableNumber(num) < 5);
          const over = sublist.filter(num => comparableNumber(num) >= 5);
          if (under.length > 0) acc.push(under);
          if (over.length > 0) acc.push(over);
          return acc;
        }, [])
    };
  });
  return tree;
}

function generate() {
  const allNums = nums.map(([num, target]) => num.toString());
  console.log(`Generating quick access menu for ${allNums.length} targets…`);
  const digitTree = getDigitTree(allNums.map(num => [num, num]));

  const docs = flattenTreeToFilesWithPages(digitTree);

  const totalPages = Object.values(docs).reduce((acc, pages) => acc + pages.length, 0);
  console.log(`Typesetting ${totalPages} pages in ${Object.keys(docs).length} docs…`);
  const files = {};
  Object.entries(docs).forEach(([doc, pages]) => {
    let name = filename;
    if (doc !== "root") {
      name += doc;
    }
    //console.log(`generating ${name}…`);
    files[`${name}.html`] = writePages(pages, name, filename);
  });
  console.log("Done!");
  return files;
}

function writePages(pages, filename, root) {
  let out = "";

  const preamble = `
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
    <a id="${filename}"></a>
  </div>
`.trimLeft();
  out += preamble;

  pages.forEach((page) => {
    const pagePreamble = `
  <div id="d${page.prefix}" style="min-height: 100vh;">

    <h2></h2>

    <h1><strong>Schnell-Schnellmenü</strong></h1>

    <div style="display: flex; justify-content: space-between;">
      <a class="tRef" href="../Text/${root}.html#d${root}">Löschen und neue Nummer aufschlagen</a>
      <a class="tRef" href="../Text/${page.prefix.length <= 2 && page.prefix !== "" ? filename.slice(0,-1) : filename}.html#d${page.prefix.slice(0,-1)}">Letzte Ziffer löschen</a>
    </div>

    <h1>${page.prefix}…</h1>
`.trimLeft();
    out += pagePreamble;

    if (Object.keys(page.digits).length > 0) {
      const nth = page.prefix.length + 1;
      const groupings = [
        [null, null, 0, null, null],
        [null, 1, 2, 3, null],
        [null, 4, 5, 6, null],
        [null, 7, 8, 9, null]
      ];

      if (groupings
          .some(row => row
            .some(digit => (
              digit !== null &&
              page["digits"].includes(digit.toString()) )))) {
        const nextPreamble = `
    <p class="oe_gross"><strong>${ordinals[nth] ? ordinals[nth] : nth.toString() + "."} Ziffer:</strong></p>

    <div class="table">
      <table>
        <tr>
`.trimLeft();
        out += nextPreamble;

        const nextRowsep = `
        </tr>

        <tr>
`.trimLeft();

        out += groupings
          .map(row => row
            .map(digit => {
              nextEntry = `
          <td>
            <p class="ctr oe_gross"><a class="tRef" href="../Text/${page.prefix.length <= 1 && digit !== null && page.digits.includes(digit.toString()) ? filename + digit.toString() : filename}.html#d${page.prefix}${digit !== null && page.digits.includes(digit.toString()) ? digit.toString() : ""}">&nbsp;&nbsp;${digit !== null && page.digits.includes(digit.toString()) ? digit.toString() : ""}&nbsp;&nbsp;</a></p>
          </td>
`.trimLeft();
              return nextEntry
            })
            .join(""))
          .join(nextRowsep);

        const nextEpilog = `
        </tr>
      </table>
    </div>
`.trimLeft();
        out += nextEpilog;
      }
    }

    if (page.direct.length) {
      const directPreamble = `
    <p><strong>Direkt aufschlagen:</strong></p>

    <div class="table">
      <table>
        <tr>
`.trimLeft();
      out += directPreamble;

      const directRowsep = `
        </tr>

        <tr>
`.trimLeft();

      out += page.direct
        .map(row => row
          .map(num => {
            const chapter = targetLookup[num];
            if (num === page.prefix) {
              const directHighlight = `
          <td>
            <p class="ctr oe_gross"><strong><a class="sRef" href="../Text/${chapter}.html#s${num}">&nbsp;${num}&nbsp;</a></strong></p>
          </td>
`.trimLeft();
              return directHighlight;
            } else {
              const directEntry = `
          <td>
            <p class="ctr"><a class="sRef" href="../Text/${chapter}.html#s${num}">&nbsp;${num}&nbsp;</a></p>
          </td>
`.trimLeft();
              return directEntry;
            }
          })
          .join(""))
        .join(directRowsep);

      const directEpilog = `
        </tr>
      </table>
    </div>
`.trimLeft();
      out += directEpilog;
    }

    const pageEpilog = `
  </div>
  <span style="page-break-after: always" />
`.trimLeft();
    out += pageEpilog;
  });

  const epilog = `
</body>
</html>
`.trimLeft();
  out += epilog;

  return out;
}

function flattenTreeToFilesWithPages(tree) {
  const files = {
    root: [
      {
        prefix: tree.prefix,
        digits: Object.keys(tree.digits),
        direct: tree.direct
      }
    ]
  };
  Object.entries(tree.digits).forEach(([digit, items]) => {
    files[digit] = [
      {
        prefix: items.prefix,
        digits: Object.keys(items.digits),
        direct: items.direct
      }
    ];
  });
  Object.entries(tree.digits).forEach(([digit, items]) => {
    if (items.digits) {
      Object.entries(items.digits).forEach(([subdigit, subitems]) => {
        files[digit+subdigit] = _flattenTreesToPages([items]);
      });
    }
  });
  return files;
}

function _flattenTreesToPages(trees) {
  if (trees.length < 1) {
    return [];
  }
  const pages = [];
  pages.push(...trees
    .map(tree => {
      return {
        prefix: tree.prefix,
        digits: Object.keys(tree.digits),
        direct: tree.direct
      };
    }));

  const list = [];
  trees.forEach(tree => {
    Object.entries(tree.digits).forEach(([digit, items]) => {
      if (items.digits || items.direct) {
        list.push(items);
      }
    });
  });
  pages.push(..._flattenTreesToPages(list));

  return pages;
}

PATCHFILES = generate(targets);
PATCHROOT = filename;
