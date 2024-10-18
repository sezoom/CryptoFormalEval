from history_run.json_store import *

logger = InteractionLogger(json_folder = os.path.join(os.getcwd(), 'dataset', 'Results', 'o1'))
logger.display_interactions(id_run=5)

logger.clean_plain()
logger.display_interactions_plain(id_run=5)

# Find output files json_output.txt and json_output_plain.txt in ./history_run folder.





