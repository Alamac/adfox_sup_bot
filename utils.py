import certifi, json, logging, re

import imapy, urllib3

import settings

def request_tickets(query, components):

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    components = str(components)
    host = 'https://st-api.yandex-team.ru/v2/issues'

    query_params = {
        'filter': 'query:' + query,
        'filter': 'components:' + components,
        'perpage': '100'
    }
    headers = {
        'Authorization': 'OAuth ' + settings.ST_AUTH_TOKEN
    }

    request = http.request('GET', host, fields=query_params, headers=headers)

    ticket_list = json.loads(request.data.decode('utf-8'))
    return ticket_list

def get_action(string):

    if string == 'Задача создана':
        return 'Task created'

    else:
        words = string.split()

        if words[0] == 'SLA':

            if 'истечёт' in words:
                return 'SLA expiring'

            elif 'нарушен' in words:
                return 'SLA expired'
        else:
            return None

def get_tickets_from_emails(host, user, ps, folder_name, del_folder_name):

    ticket_list = []

    mail = imapy.connect(host = host,
                 username = user,
                 password = ps,
                 ssl= True)

    emails = mail.folder(folder_name).emails()
    
    if emails:
        
        for em in emails:
            subject = em['subject']

            try:

                ticket = re.findall(r'ADFOX-\d*|PISUP-\d*', subject)[0]
                url = f'https://st.yandex-team.ru/{ticket}'
                action = re.findall(r'^\[(.*?)\]', subject)[0]
                action = get_action(action)
                theme = re.findall(r'\) (.*?) \[ST\]$', subject)[0]
                ticket_list.append({
                    'ticket': ticket,
                    'url': url,
                    'action': action,
                    'theme': theme
                })
                em.move(del_folder_name)
            except IndexError:
                pass

    mail.logout()

    return ticket_list