from gi.repository import GObject, Gedit, Gtk, Gdk

class VimMotionPlugin(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "VimMotionPlugin"

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)
        self.css_provider = Gtk.CssProvider()
        self.vim_mode = False
        self.update_status_bar(self.vim_mode)
        self.numeric_input = ''

    def do_activate(self):
        self.view.connect('key-press-event', self.on_key_press)

    def do_deactivate(self):
        pass

    def do_update_state(self):
        pass

    def update_status_bar(self, vim_mode):
        self.update_highlight_style(vim_mode)
        statusbar = self.view.get_toplevel().get_statusbar()
        context_id = statusbar.get_context_id("VimMode")

        if vim_mode:
            self.status_message_id = statusbar.push(context_id, "Vim mode")
        else:
            if hasattr(self, 'status_message_id'):
                statusbar.remove(context_id, self.status_message_id)

    def update_highlight_style(self, vim_mode):
        style_context = self.view.get_style_context()

        if vim_mode:
            css = b'.view { background-color: #F0E68C; }'
            self.css_provider.load_from_data(css)
            style_context.add_provider(self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        else:
            style_context.remove_provider(self.css_provider)

    def on_key_press(self, widget, event):
        keyval = Gdk.keyval_name(event.keyval)
        state = event.state

        if keyval == 'Escape':
            if not self.vim_mode:
                self.vim_mode = True
                self.numeric_input = ''
                self.update_status_bar(self.vim_mode)
            return True

        if self.vim_mode:
            shift_pressed = state & Gdk.ModifierType.SHIFT_MASK
            return self.handle_vim_mode(keyval, shift_pressed)
        else:
            return False

    def handle_vim_mode(self, keyval, shift_pressed):
        buffer = self.view.get_buffer()

        if keyval == 'I' or (keyval == 'i' and shift_pressed):
            self.move_cursor_to_line_start()
            self.vim_mode = False
            self.update_status_bar(self.vim_mode)
            return True
        elif keyval == 'A' or (keyval == 'a' and shift_pressed):
            self.move_cursor_to_line_end()
            self.vim_mode = False
            self.update_status_bar(self.vim_mode)
            return True
        elif keyval == 'a':
            self.move_cursor_forward()
            self.vim_mode = False
            self.update_status_bar(self.vim_mode)
            return True
        elif keyval == 'i':
            # Switch to insert mode (normal Gedit functionality)
            self.vim_mode = False
            self.update_status_bar(self.vim_mode)
            return True
        elif keyval.isdigit():
            # Accumulate numeric input
            self.numeric_input += keyval
            return True
        elif keyval in ['h', 'j', 'k', 'l']:
            count = int(self.numeric_input) if self.numeric_input else 1
            self.move_cursor(buffer, keyval, count)
            self.numeric_input = ''  # Reset numeric input after motion
            return True

        return False

    def move_cursor(self, buffer, keyval, count):
        iter = buffer.get_iter_at_mark(buffer.get_insert())
        for _ in range(count):
            if keyval == 'h' and not iter.starts_line():
                iter.backward_char()
            elif keyval == 'l' and not iter.ends_line():
                iter.forward_char()
            elif keyval == 'j':
                iter.forward_line()
            elif keyval == 'k':
                iter.backward_line()

        buffer.place_cursor(iter)
        self.view.scroll_to_iter(iter, 0, True, 0, 0)

    def move_cursor_to_line_start(self):
        buffer = self.view.get_buffer()
        iter = buffer.get_iter_at_mark(buffer.get_insert())
        iter.set_line_offset(0)
        buffer.place_cursor(iter)

    def move_cursor_to_line_end(self):
        buffer = self.view.get_buffer()
        iter = buffer.get_iter_at_mark(buffer.get_insert())
        iter.forward_to_line_end()
        buffer.place_cursor(iter)

    def move_cursor_forward(self):
        buffer = self.view.get_buffer()
        iter = buffer.get_iter_at_mark(buffer.get_insert())
        if not iter.ends_line():
            iter.forward_char()
        buffer.place_cursor(iter)

