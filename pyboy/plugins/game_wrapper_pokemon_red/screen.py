from .utils import fill_range, sequence_in, read_range, String, press_a


def cursor_position(self, index=None):
    """Returns the current cursor position
    
    Parameters
    ----------
    index: `int`, optional
        The new index; default None
    Returns
    -------
    `int`:
        The current cursor positio n
    
    """
    if index:
        self.pyboy.set_memory_value(0xCC26, index)
    return self.pyboy.get_memory_value(0xCC26)

def skip_text_box(self):
    """Skips the current textbox"""
    if self.yes_no_box_shown() or self.select_box_shown() or not self.text_box_shown():
        return
    press_a(self.pyboy)
def text_box_shown(self) -> bool:
    """Whether a textbox is currently shown in the screen or not
    
    Returns
    --------
    `bool`:
        Whether a textbox is shown
    """
    return read_range(self.pyboy, 0xC490, 20) == [0x79, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7a, 0x7b]
def current_frame_text_box_content(self, value=None) -> str:
    """The textbox cotent in the current frame.
    Parameters
    ----------
    value: `str`, optional
        The new content of the textbox; default None
    Returns
    -------
    `str`:
        The content
    
    """
    if value:
        box_start = 0xC4A4
        lines = []
        cur_line = []
        for i, s in enumerate(value):
            if i % 18 == 0 and i != 0:
                lines.append(cur_line)
                cur_line = [s]
                continue
            cur_line.append(s)
        # if cur_line is still holding a value
        if len(cur_line) > 0:
            lines.append(cur_line)
        if len(lines) < 2:
            [lines.append([]) for _ in range(2-len(lines))]

        fill_range(self.pyboy, box_start+1, [0x7F] * 18)

        cur_line_index = 0
        for line in lines[:2]:
            cur_line_index += 1
            encoded = String.encode_string(line)
            fill_range(self.pyboy, (box_start+1) + 20 * cur_line_index, encoded + [0x7F] * ((18 if cur_line_index == 1 else 17) - len(encoded)))
            # 18 if cur_line == 1 else 17 = let the wait_for button char or whatever show up
            if cur_line_index == 1:
                fill_range(self.pyboy, (box_start+1) + 20 * (cur_line_index+1), [0x7F] * (18 if cur_line == 1 else 17))
            cur_line_index += 1

        # fill_range(pyboy, 0xC4A4 + 20, String.encode_string(value))
    return String.decode_bytes(read_range(self.pyboy, 0xC4A4, 80))
def text_box_content(self, value=None):
    """The current content of the displayed textbox
        
    This function will wait until the textbox finished. 
    If you want the content of the textbox in the current frame, 
    use the `.current_frame_text_box_content` function
    
    Parameters
    ----------
    value: `str`, optional
        The new textbox content; default None
    Returns
    -------
    `str`:
        The textbox content
    
    """
    self.wait_for_textbox_finish()
    if value:
        self.current_frame_text_box_content(value)
    return self.current_frame_text_box_content()
def wait_for_textbox_finish(self):
    """Waits for the textbox to finish displaying text"""
    # functiton for preventing unfinished text because of text "animation"
    last_box = self.current_frame_text_box_content()
    [self.pyboy.tick() for _ in range(10)]
    cur_box = self.current_frame_text_box_content()
    if last_box != cur_box:
        self.wait_for_textbox_finish()

# C430
#   1       0x79 0x7A 0x7A 0x7A 0x7A 0x7B
#   2       0x7C 0x7F 0x7F 0x7F 0x7F 0x7C
#   3       0x7C ...  ...  ...  ...  0x7C
#   4       0x7C 0x7F 0x7F 0x7F 0x7F 0x7C
#   5       0x7C ...  ...  ...  ...  0x7C
#   6       0x7D 0x7A 0x7A 0x7A 0x7A 0x7E
# state 3
def yes_no_box_shown(self) -> bool:
    """Whether a yes no box is shown
    
    Returns
    -------
    `bool`:
        Is a yes no box shown?
    
    """
    return (
        # line 1 (border only)
        sequence_in([0x79] + ([0x7A]*4) + [0x7B], read_range(self.pyboy, 0xC430, 20))
            and
        # line 2
        read_range(self.pyboy, 0xC44E) == [0x7C] and read_range(self.pyboy, 0xC453) == [0x7C]
            and
        # line 3 (empty)
        read_range(self.pyboy, 0xC462, 6) == [0x7C] + ([0x7F]*4) + [0x7C]
            and
        # line 4
        read_range(self.pyboy, 0xC476) == [0x7C] and read_range(self.pyboy, 0xC47B) == [0x7C]
            and
        # line 5 (last) (border only)
        sequence_in([0x7D] + ([0x7A]*4) + [0x7E], read_range(self.fpyboy, 0xC430+80, 20))
    )
def select_yes_no(self, yes=True):
    """Selects a choice in a yes no box
    
    Parameters
    ----------
    yes: `bool`, optional
        If yes should be selected (``True``) or no (``False``); default ``True``
    
    """
    self.cursor_position(int(not yes))
    press_a(self.pyboy)

# state 5
def select_box_shown(self) -> bool:
    """Whether a selection menu is shown

    Returns
    --------
    `bool`:
        is select menu shown
    
    """
    line1 = read_range(self.pyboy, 0xC3A0, 20)
    line2 = read_range(self.pyboy, 0xC3A0+20, 20)
    line3 = read_range(self.pyboy, 0xC3A0+40, 20)
    return (
        # line 1
            (
                # upper border
                line1[:3] == [0x79, 0x7A, 0x7A] 
                    and
                # next line is empty line wiht border +min of 3 emptys
                sequence_in(([0x7A] * 3) + [0x7B], line1)
            )
        and
            # line 2
            (
                # next line ends with empty line with min of 3 emptys + border
                sequence_in([0x7C] + ([0x7F] * 3), line2)
                    and
                # first line ends with border
                sequence_in(([0x7F] * 3) + [0x7C], line2)
            )
        and
            # line 3
            (
                line3[0] == 0x7C
            )
    )
def select_box_items(self, return_header=False):
    """The select box items
    
    Parameters
    ----------
    return_header: `bool`, optional
        Whether a tuple together with the header should be returned; default False
    
    Returns
    -------
    List[`str`]:
        The select box items

    If return_header is `True`:
        Tuple[List[`str`], `str`]:
            `[0]`: The items of the select box
            `[1]`: The heading of the select box
    
    """
    # all lines
    start = 0xC3A0
    lines = []
    header_text = String.decode_bytes([x for x in read_range(self.pyboy, start, 20) if x not in [0x7A, 0x79]])
    # getting end of select menu
    for i in range(0xD000): # max lines of screen
        start += 20
        cur_line = read_range(self.pyboy, start, 20)
        if cur_line[:3] == [0x7D, 0x7A, 0x7A] and sequence_in([0x7A, 0x7A, 0x7E], cur_line):
            break
        lines.append(cur_line)
    text_lines = [line for line in lines if not sequence_in([0x7C] + ([0x7F] * 4), line[:5])]
    decoded = [String.decode_bytes(line) for line in text_lines]
    if return_header is True:
        return (decoded, header_text)
    return decoded
def select_in_box(self, index=0):
    """Selects an item in a select box
    
    Parameters
    ----------
    index: `int`, optional
        The index of the item that should be selected; default ``0``
    
    """
    self.cursor_position(index)
    press_a(self.pyboy)