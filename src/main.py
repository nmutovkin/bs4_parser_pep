from bs4 import BeautifulSoup
from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, EXPECTED_STATUS, HEADER_LATEST, HEADER_PEP,
                       HEADER_WHATS_NEW, MAIN_DOC_URL, PEP_URL)
import logging
from outputs import control_output
import re
import requests_cache
from tqdm import tqdm
from urllib.parse import urljoin
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    response = get_response(session, whats_new_url)
    if response is None:
        return None

    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})

    results = [HEADER_WHATS_NEW]

    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        response = get_response(session, version_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')

        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return None

    soup = BeautifulSoup(response.text, 'lxml')

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    results = [HEADER_LATEST]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)

        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''

        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return None

    soup = BeautifulSoup(response.text, 'lxml')

    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a',
                          {'href': re.compile(r'.+pdf-a4\.zip$')})

    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEP_URL)
    if response is None:
        return None

    soup = BeautifulSoup(response.text, 'lxml')
    num_index = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    peps = num_index.find_all('td', attrs={'class': 'num'})

    results = [HEADER_PEP]
    logging.info('Несовпадающие статусы:')

    status_counts = {}
    total_count = 0

    for pep in tqdm(peps):
        status_table = pep.find_previous_sibling('td').string[1:]
        pep_num_a_tag = pep.find('a')
        href = pep_num_a_tag['href']
        pep_num_link = urljoin(PEP_URL, href)

        response = get_response(session, pep_num_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, 'lxml')
        status_tag = find_tag(soup, 'dt',
                              string='Status').find_next_sibling('dd')

        status_page = status_tag.string

        # statuses are not consistent
        if status_page not in EXPECTED_STATUS[status_table]:
            logging.info((f'{pep_num_link}\nСтатус в карточке: {status_page}\n'
                          f'Ожидаемые статусы: {EXPECTED_STATUS[status_table]}'
                          ))

        if status_page not in status_counts.keys():
            status_counts[status_page] = 1
        else:
            status_counts[status_page] += 1

        total_count += 1

    results += ([(str(k), str(v)) for k, v in status_counts.items()] +
                [('Total', total_count)])

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
