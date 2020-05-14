# to show data at the end
def save_data(save_list):
    data_list = list()

    for key, value in save_list.items():
        data_list.append('{} - {}'.format(key, value))

    return "\n".join(data_list).join(['\n', '\n'])

