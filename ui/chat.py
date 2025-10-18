import pygame

import pygame.font

class ChatUI:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.is_chat_open = False
        
        # Chat history
        self.messages = []
        self.max_messages = 50
        self.scroll_offset = 0
        
        # Input box
        self.input_text = ""
        self.input_active = False
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # Colors
        self.bg_color = (0, 0, 0, 180)
        self.border_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.input_bg_color = (50, 50, 50)
        self.input_active_color = (70, 70, 70)
        
        # Layout
        self.padding = 10
        self.input_height = 30
        self.message_height = 20

    def _message_area_rect(self):
        return pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y + self.padding,
            self.rect.width - 2 * self.padding,
            self.rect.height - self.input_height - 3 * self.padding
        )

    def _input_rect(self):
        return pygame.Rect(
            self.rect.x + self.padding,
            self.rect.bottom - self.input_height - self.padding,
            self.rect.width - 2 * self.padding,
            self.input_height
        )
    
    def toggle_chat(self):
        """Toggle chat open/closed"""
        self.is_chat_open = not self.is_chat_open
        if not self.is_chat_open:
            self.input_active = False
            self.input_text = ""
            self.cursor_pos = 0
        else:
            self.input_active = True
            self.cursor_timer = 0
        self.scroll_offset = 0  # <— reset
    
    def open_chat(self):
        """Open the chat"""
        self.is_chat_open = True
        self.input_active = True
        self.input_text = ""
        self.cursor_pos = 0
        self.scroll_offset = 0  # <— reset
        
    def close_chat(self):
        """Close the chat"""
        self.is_chat_open = False
        self.input_active = False
        self.input_text = ""
        self.cursor_pos = 0
        self.scroll_offset = 0  # <— reset
        
    def add_message(self, username, message, color=(255, 255, 255)):
        """Add a message to the chat"""
        self.messages.append({
            'username': username,
            'message': message,
            'color': color
        })
        
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            # Toggle chat with T key (or any key you prefer)
            if event.key == pygame.K_t and not self.input_active:
                self.toggle_chat()
                if self.is_chat_open:
                    self.input_active = True
                return None
            
            # Handle escape to close chat
            if event.key == pygame.K_ESCAPE:
                if self.is_chat_open:
                    self.close_chat()
                    return None
            
            # Only handle input if chat is open
            if self.is_chat_open and self.input_active:
                if event.key == pygame.K_RETURN:
                    # Send message
                    if self.input_text.strip():
                        message = self.input_text.strip()
                        self.input_text = ""
                        self.cursor_pos = 0
                        return message
                    self.input_text = ""
                    self.cursor_pos = 0
                elif event.key == pygame.K_BACKSPACE:
                    if self.cursor_pos > 0:
                        self.input_text = self.input_text[:self.cursor_pos-1] + self.input_text[self.cursor_pos:]
                        self.cursor_pos -= 1
                elif event.key == pygame.K_DELETE:
                    if self.cursor_pos < len(self.input_text):
                        self.input_text = self.input_text[:self.cursor_pos] + self.input_text[self.cursor_pos+1:]
                elif event.key == pygame.K_LEFT:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif event.key == pygame.K_RIGHT:
                    self.cursor_pos = min(len(self.input_text), self.cursor_pos + 1)
                elif event.key == pygame.K_HOME:
                    self.cursor_pos = 0
                elif event.key == pygame.K_END:
                    self.cursor_pos = len(self.input_text)
                else:
                    # Add character
                    if len(event.unicode) > 0 and event.unicode.isprintable():
                        self.input_text = self.input_text[:self.cursor_pos] + event.unicode + self.input_text[self.cursor_pos:]
                        self.cursor_pos += 1

        elif event.type == pygame.MOUSEWHEEL and self.is_chat_open:
            # Only scroll if mouse is over the chat's message area
            if self._message_area_rect().collidepoint(pygame.mouse.get_pos()):
                # Compute how many messages fit
                message_area_height = self.rect.height - self.input_height - 5 * self.padding
                visible = max(1, int(message_area_height // self.message_height))
                max_offset = max(0, len(self.messages) - visible)

                # Pygame: event.y > 0 means scroll up → older messages → increase offset
                self.scroll_offset = max(0, min(max_offset, self.scroll_offset - event.y))

                                
        elif event.type == pygame.MOUSEBUTTONDOWN and self.is_chat_open and event.button == 1:
            # Check if clicked on input box
            input_rect = self._input_rect()
            message_rect = self._message_area_rect()
            self.input_active = input_rect.collidepoint(event.pos)
            if not self.input_active and not message_rect.collidepoint(event.pos):
                self.close_chat()
        
        return None
    
    def update(self, dt):
        """Update cursor blinking"""
        if self.is_chat_open:
            self.cursor_timer += dt
            if self.cursor_timer >= 500:  # Blink every 500ms
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
    
    def draw(self, screen):
        """Draw the chat UI"""
        if not self.is_chat_open:
            return
            
        # Create surface with alpha for transparency
        chat_surface = pygame.Surface((self.rect.width, self.rect.height))
        chat_surface.set_alpha(180)
        chat_surface.fill((0, 0, 0))
        
        # Draw border
        pygame.draw.rect(chat_surface, self.border_color, chat_surface.get_rect(), 2)
        
        # Draw messages
        message_area_height = self.rect.height - self.input_height - 3 * self.padding
        available_width = self.rect.width - 2 * self.padding
        
        # Calculate how many lines all messages will take
        total_lines = 0
        message_lines = []
        
        for msg in self.messages:
            # Calculate username width
            username_text = f"{msg['username']}: "
            username_width = self.small_font.size(username_text)[0]
            message_width = available_width - username_width
            
            # Wrap message text
            words = msg['message'].split(' ')
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if self.small_font.size(test_line)[0] <= message_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        # Word is too long, break it
                        lines.append(word)
            
            if current_line:
                lines.append(current_line)
            
            message_lines.append({
                'username': msg['username'],
                'lines': lines,
                'color': msg['color'],
                'username_width': username_width
            })
            total_lines += len(lines)

        # Calculate visible lines and scrolling
        visible_lines = max(1, int(message_area_height // self.message_height))
        max_offset = max(0, total_lines - visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_offset))

        # Draw messages
        current_line = 0
        start_y = self.padding
        
        for msg_data in message_lines:
            for i, line in enumerate(msg_data['lines']):
                # Check if this line should be visible
                if current_line >= self.scroll_offset and current_line < self.scroll_offset + visible_lines:
                    y_pos = start_y + (current_line - self.scroll_offset) * self.message_height
                    
                    if i == 0:  # First line shows username
                        # Draw username
                        username_surface = self.small_font.render(f"{msg_data['username']}: ", True, msg_data['color'])
                        chat_surface.blit(username_surface, (self.padding, y_pos))
                        
                        # Draw message line
                        message_surface = self.small_font.render(line, True, self.text_color)
                        chat_surface.blit(message_surface, (self.padding + msg_data['username_width'], y_pos))
                    else:  # Continuation lines are indented
                        message_surface = self.small_font.render(line, True, self.text_color)
                        chat_surface.blit(message_surface, (self.padding + msg_data['username_width'], y_pos))
                
                current_line += 1
        
        # Draw input box
        input_rect = pygame.Rect(
            self.padding,
            self.rect.height - self.input_height - self.padding,
            self.rect.width - 2 * self.padding,
            self.input_height
        )
        
        input_color = self.input_active_color if self.input_active else self.input_bg_color
        pygame.draw.rect(chat_surface, input_color, input_rect)
        pygame.draw.rect(chat_surface, self.border_color, input_rect, 1)
        
        # Draw input text
        if self.input_text or self.input_active:
            text_surface = self.font.render(self.input_text, True, self.text_color)
            chat_surface.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            
            # Draw cursor
            if self.input_active and self.cursor_visible:
                cursor_x = input_rect.x + 5
                if self.cursor_pos > 0:
                    cursor_text = self.input_text[:self.cursor_pos]
                    cursor_width = self.font.size(cursor_text)[0]
                    cursor_x += cursor_width
                
                pygame.draw.line(chat_surface, self.text_color, 
                               (cursor_x, input_rect.y + 3), 
                               (cursor_x, input_rect.bottom - 3), 1)
        else:
            # Draw placeholder text
            placeholder = self.font.render("Type a message...", True, (128, 128, 128))
            chat_surface.blit(placeholder, (input_rect.x + 5, input_rect.y + 5))
        
        # Blit to main screen
        screen.blit(chat_surface, self.rect.topleft)

    def is_open(self):
        return self.is_chat_open