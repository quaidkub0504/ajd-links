"""Sync the Google rating and review count on index.html with ajdanboise.com.

Reads the Trustindex Google-reviews widget on the main site, then rewrites every
<... data-rating> and <... data-count> element in index.html. Exits non-zero
(without touching the file) if the numbers can't be found or look wrong.
"""
import re
import sys
import urllib.request

SOURCE = "https://ajdanboise.com/"
PAGE = "index.html"

req = urllib.request.Request(SOURCE, headers={"User-Agent": "Mozilla/5.0 (links.ajdanboise.com review sync)"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

rating_m = re.search(r'rating">\s*([0-5]\.[0-9])\s*<', html)
count_m = re.search(r'rating-reviews">\s*([0-9][0-9,]*)\s+reviews', html)
if not rating_m or not count_m:
    sys.exit("Could not find the rating/review count on ajdanboise.com; the widget may have changed.")

rating = rating_m.group(1)
count = int(count_m.group(1).replace(",", ""))
if not (1.0 <= float(rating) <= 5.0) or count < 100:
    sys.exit(f"Refusing implausible values: rating={rating} count={count}")

page = open(PAGE, encoding="utf-8").read()
new = re.sub(r"(<(?:b|span) data-rating>)[^<]*(</(?:b|span)>)", rf"\g<1>{rating}\g<2>", page)
new = re.sub(r"(<span data-count>)[^<]*(</span>)", rf"\g<1>{count:,}\g<2>", new)

if new == page:
    print(f"No change: {rating} stars, {count:,} reviews")
else:
    open(PAGE, "w", encoding="utf-8", newline="").write(new)
    print(f"Updated: {rating} stars, {count:,} reviews")
