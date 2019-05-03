from IPython.core.magic import register_line_magic, register_cell_magic
from trello import TrelloClient

status_dict = {'todo':0, 'doing':1, 'done':2}

trello_list_id = ''
trello_api_key = ''
trello_token = ''

#                 Todo                        Doing                       Done
trello_labels = ['', '', ''] # Add your own labels.

# Trello
client = TrelloClient(
    api_key=trello_api_key,
    token=trello_token
)

def update_checklist(arr, checklist):
	# Remove checklist elements not in arr
	for item in checklist.items:
		if item['name'] in arr: # Remove so not added twice.
			arr.remove(item['name'])
			temp += 'Removed (from arr) ' + item + '\n'
		else:
			checklist.delete_checklist_item(item['name'])
			temp += 'Removed (from checklist)  ' + item + '\n'
	# Add checklist elements in arr (that are not already present)
	for item in arr:
		checklist.add_checklist_item(item)
		temp += 'Added ' + item + '\n'

def get_status(str):
	if str.isdigit():
		return int(str)
	elif str in status_dict:
		return status_dict[str]
	return -1

@register_cell_magic
def info(line, cell):
	file_name = cell.split("\n")[0]
	status = get_status(cell.split("\n")[1])
	if status < 0 or status > 2: # Invalid status
		return
	tag = list(map(str.strip, cell.split("\n")[2].split(",")))
	ingest = list(map(str.strip, cell.split("\n")[3].split(",")))
	# print(tags)
	# print(ingest)
	trello_list = client.get_list(trello_list_id)

	for card in trello_list.list_cards():
		if card.name == file_name and not card.closed: # Card found
			# Checklists
			for checklist in card.fetch_checklists():
				if checklist.name == "Tag":
					update_checklist(tag, checklist)
				elif checklist.name == "Ingest":
					update_checklist(ingest, checklist)
			
			# Label
			for label in trello_labels:
				card.remove_label(Label(None, label, None))

			card.add_label(Label(None, trello_labels[status], None))
			print("OK")
			return

	# Card not found... create one
	card = trello_list.add_card(file_name, file_name, [Label(None, trello_labels[status], None)])
	card.add_checklist("Tag", tag)
	card.add_checklist("Ingest", ingest)
	print("OK")
	return