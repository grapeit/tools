import sys
import subprocess
import re

args = sys.argv
if len(args) != 2:
    print("device name expected")
    exit(1)

KB = 1024
MB = KB * 1024
GB = MB * 1024
TB = GB * 1024


def getValue(val, unit):
    v = float(val)
    if unit == "TB":
        v *= TB
    elif unit == "GB":
        v *= GB
    elif unit == "MB":
        v *= MB
    elif unit == "KB":
        v *= KB
    return v


def parseUsage(data):
    read, written, used = 0, 0, 0
    for ln in data.split("\n"):
        m = re.match(r"Data Units (?P<op>\w+): *.+\[(?P<val>[\d\.]+) (?P<unit>\w+)\]", ln)
        if m:
            if m.group("op") == "Read":
                read = getValue(m.group("val"), m.group("unit"))
            elif m.group("op") == "Written":
                written = getValue(m.group("val"), m.group("unit"))
        else:
            m = re.match(r"Percentage Used: *(?P<val>\w+)", ln)
            if m:
                used = float(m.group("val"))
    return read, written, used


def formatSize(value):
    if value > TB:
        return "%lg TB" % (value / TB)
    elif value > GB:
        return "%lg GB" % (value / GB)
    elif value > MB:
        return "%lg MB" % (value / MB)
    elif value > KB:
        return "%lg KB" % (value / KB)
    return value


sp = subprocess.run(["smartctl", "-a", "/dev/" + args[1]], stdout=subprocess.PIPE)
usage = parseUsage(sp.stdout.decode())

print("Read: ", formatSize(usage[0]))
print("Written: ", formatSize(usage[1]))
print("Total: ", formatSize(usage[0] + usage[1]))
print("Used: %.0f%%" % usage[2])
