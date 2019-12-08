import sys
from socket import socket, AF_INET, SOCK_DGRAM


class Member:
    """
    A class used to represent a participant in the chat.

    Attributes
    ----------
    name : str
        The name of the member.
    port : int
        The port number of the member.
    pending_messages : array of strings
        The messages that are waiting for the member.
    """
    def __init__(self, name, port):
        """
        Parameters
        ----------
        name : str
            The name of the member.
        port : int
            The port number of the member.
        """
        self.name = name
        self.port = port
        self.pending_messages = []

    def add_message(self, message):
        """
        Adds a new message to the member's pending messages list.

        Parameters
        ----------
        message : str
            The message to add to the pending messages list.
        """
        self.pending_messages.append(message)

    def clear_message_board(self):
        """
        Clears the member's pending messages list.
        """
        self.pending_messages = []


def find_member_by_info(chat_members, sender_info):
    """
    Returns a member object from the members list by the port number.

    Parameters
    ----------
    chat_members : list
        The current online members.
    sender_info : str, int
        IP address and port number of the sender.

    Returns
    -------
    Member
        The specific member.
    """
    # find the relevant member in member list by port number.
    for m in chat_members:
        if sender_info[1] == m.port:
            return m


def is_port_available(chat_members, sender_info):
    """
    Checks if a port number is taken by a member's connection.

    Parameters
    ----------
    chat_members : list
        The current online members.
    sender_info : str, int
        IP address and port number of the sender.

    Returns
    -------
    bool
        If port is available.
    """
    for m in chat_members:
        if m.port == sender_info[1]:
            return False
    return True


def merge_str(substr):
    """
    Removes the prefix of the message type and merges the rest of the message to a new string.

    Parameters
    ----------
    substr : list
        List of message components.

    Returns
    -------
    str
        Merged message (without the type prefix).
    """
    # remove the first element (which is the type of the message).
    substr.pop(0)
    # merge the rest of the substrings.
    new_str = ""
    for sub in substr:
        new_str += sub + " "
    new_str = new_str[:-1]
    return new_str

def display_other_members(sender_info, chat_members):
    """
    Creates a string of the chat members that are currently online (without the sender).

    Parameters
    ----------
    sender_info: str, int
        IP address and port number of the sender.
    chat_members : list
        The current online members.

    Returns
    -------
    str
        Members separated by ','.
    """
    name_list = []
    member = find_member_by_info(chat_members, sender_info)
    for m in chat_members:
        if m != member:
            name_list.append(m.name)
    separator = ", "
    if len(chat_members) == 1:
        return ""
    return separator.join(name_list)


def join_group(substr, sender_info, chat_members):
    """
    Adds a new member to the chat members list.

    Parameters
    ----------
    substr : list
        List of message components.
    sender_info: str, int
        IP address and port number of the sender.
    chat_members : list
        The current online members.
    """
    # create a message to inform other members.
    name = merge_str(substr)
    for m in chat_members:
        m.add_message(name + " has joined")
    # create a new member and add it to list. then send him an empty message.
    member = Member(name, sender_info[1])
    chat_members.append(member)
    other_members = display_other_members(sender_info, chat_members)
    s.sendto(other_members.encode(), sender_info)


def send_message(substr, sender_info, chat_members):
    """
    Adds a new message to the participants' pending message lists (except of the sender).

    Parameters
    ----------
    substr : list
        List of message components.
    sender_info: str, int
        IP address and port number of the sender.
    chat_members : list
        The current online members.
    """
    member = find_member_by_info(chat_members, sender_info)
    name = member.name
    message = merge_str(substr)
    full_message = name + ": " + message
    # send the message to the other members.
    for m in chat_members:
        if m.name != name:
            m.add_message(full_message)
    # send all the pending messages to the sender.
    refresh_messages(sender_info, chat_members)


def change_name(substr, sender_info, chat_members):
    """
    Changes the name of the sender in the chat members list, and notifies other members of the change.

    Parameters
    ----------
    substr : list
        List of message components.
    sender_info: str, int
        IP address and port number of the sender.
    chat_members : list
        The current online members.
    """
    member = find_member_by_info(chat_members, sender_info)
    old_name = member.name
    new_name = merge_str(substr)
    # create message and add it to other members' message board.
    message = old_name + " changed his name to " + new_name
    for m in chat_members:
        if sender_info[1] != m.port:
            m.add_message(message)
        else:
            m.name = new_name
    # send all the pending messages to the sender.
    refresh_messages(sender_info, chat_members)


def leave_group(sender_info, chat_members):
    """
    Removes the sender from the chat members list, and notifies the other members.

    Parameters
    ----------
    sender_info: str, int
        IP address and port number of the sender.
    chat_members : list
        The current online members.
    """
    member = find_member_by_info(chat_members, sender_info)
    name = member.name
    chat_members.remove(member)
    # inform other members.
    for m in chat_members:
        m.add_message(name + " has left the group")
    empty_msg = ""
    s.sendto(empty_msg.encode(), sender_info)


def refresh_messages(sender_info, chat_members):
    """
    Displays the pending messages of the member.

    Parameters
    ----------
    sender_info: str, int
        IP address and port number of the sender.
    chat_members : list
        The current online members.
    """
    member = find_member_by_info(chat_members, sender_info)
    # if pending message list is empty, return empty message.
    if len(member.pending_messages) == 0:
        empty_msg = ""
        s.sendto(empty_msg.encode(), sender_info)
        return
    # if there are pending messages, send them.
    final_msg = ""
    for msg in member.pending_messages:
        final_msg += msg + "\n"
    s.sendto(final_msg.encode(), sender_info)
    # after sending all messages, clear message board.
    member.clear_message_board()


def handle_message(message, sender_info, chat_members):
    """
    Handles the message by its' type prefix.
    1 = Join group
    2 = Send message
    3 = Change name
    4 = Leave group
    5 = Show pending messages

    Parameters
    ----------
    substr : list
        List of message components.
    sender_info: str, int
        IP address and port number of the sender.
    chat_members : list
        The current online members.       
    """
    substr = message.split(' ')
    if substr[0] == "1":
        # if a member already registered to the port, don't allow new registrastions.
        if not is_port_available(chat_members, sender_info):
            illegal_msg = "Illegal request"
            s.sendto(illegal_msg.encode(), sender_info)
            return
        join_group(substr, sender_info, chat_members)
        return
    # don't allow sending messages if member did not register.
    if is_port_available(chat_members, sender_info):
        illegal_msg = "Illegal request"
        s.sendto(illegal_msg.encode(), sender_info)
        return
    if substr[0] == "2":
        send_message(substr, sender_info, chat_members)
        return
    if substr[0] == "3":
        change_name(substr, sender_info, chat_members)
        return
    if substr[0] == "4":
        leave_group(sender_info, chat_members)
        return
    if substr[0] == "5":
        refresh_messages(sender_info, chat_members)
        return
    illegal_msg = "Illegal request"
    s.sendto(illegal_msg.encode(), sender_info)


s = socket(AF_INET, SOCK_DGRAM)
source_ip = '0.0.0.0'
source_port = int(sys.argv[1])
s.bind((source_ip, source_port))
chat_members = []
while True:
    message, sender_info = s.recvfrom(2048)
    handle_message(message.decode(), sender_info, chat_members)
