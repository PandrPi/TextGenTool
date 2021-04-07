import curses

from helper import safe_cast

src: curses.window = curses.initscr()
src.scrollok(1)
curses.start_color()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)


def close():
    src.clear()
    src.refresh()
    curses.endwin()


def write(*args):
    src.addstr(*args)
    src.refresh()


def write_formatted(format_str: str, *args):
    """
    Formatted string writing

    Example:
    format_string = "{0,2} + {1,3} = {2,4}"
    args = [a, b, c]

    The written string will be "a + b = c", but 'a' will be green, 'b' - yellow and 'c' - red colored
    :return:
    """

    from copy import deepcopy

    if len(args) != format_str.count('{') and len(args) != format_str.count('}'):
        raise Exception("Number of braces and number of args are not equal!!!")

    format_str = deepcopy(format_str)

    strings = []
    brace_list = [('', 0)]
    for i in range(format_str.count('{')):
        start, end = (format_str.index('{'), format_str.index('}'))
        cut_part = format_str[start: end + 1]
        brace_list.append((cut_part, start))
        format_str = format_str.replace(brace_list[i + 1][0], '')
        temp = brace_list[len(brace_list) - 2][1]
        strings.append((format_str[temp:start], 1))

        pair = [int(i.strip()) for i in cut_part[1:-1].split(',')]
        strings.append((str(args[i]), 1 if len(pair) < 2 else pair[1]))

    brace_list.pop(0)
    if brace_list[len(brace_list) - 1][1] != len(format_str):
        strings.append((format_str[brace_list[len(brace_list) - 1][1]:], 1))

    for part in strings:
        src.addstr(part[0], curses.color_pair(part[1]))
    src.refresh()


def read(caption: str = ''):
    write(caption)
    curses.cbreak()
    curses.noecho()
    input_str, c = '', ''

    while c != 10:
        c = src.getch()
        c_str = str(safe_cast(c, chr, ''))
        if c == 8 or c == 127 or c == curses.KEY_BACKSPACE:
            if len(input_str) != 0:
                src.addstr("\b \b")
                input_str = input_str[:-1]
        elif (c_str.isprintable() and c_str.isdecimal()) or c == 10:
            src.addstr(c_str)
            input_str += c_str

    curses.echo()
    curses.nocbreak()
    return input_str.replace('\n', '')


# Demonstrate how to move the cursor one position to the left
def move_left():
    y, x = src.getyx()
    src.move(y, x - 1)


# Demonstrate how to move the cursor one position to the right
def move_right():
    y, x = src.getyx()
    src.move(y, x + 1)


# Demonstrate how to move the cursor up one line (without affecting its horizontal position)
def move_up():
    y, x = src.getyx()
    src.move(y - 1, x)


#    Demonstrate how to move the cursor down one line (without affecting its horizontal position)
def move_down():
    y, x = src.getyx()
    src.move(y + 1, x)


# Demonstrate how to move the cursor to the beginning of the line
def move_line_home(y_offset: int = 0):
    y, x = src.getyx()
    src.move(y + y_offset, 0)
    src.clrtoeol()


# Demonstrate how to move the cursor to the end of the line
def move_line_end():
    y, x = src.getyx()
    maxy, maxx = src.getmaxyx()
    src.move(y, maxx)


# Demonstrate how to move the cursor to the top left corner of the screen
def move_page_home():
    src.move(0, 0)


# Demonstrate how to move the cursor to the bottom right corner of the screen
def move_page_end():
    y, x = src.getmaxyx()
    src.move(y, x)
