import re

__all__ = (
    'get_dict_from_dl',
)


def _dl_generator(dl, first_text=False):
    for item in dl:
        if item.name == 'dt':
            cur_text = item.get_text(strip=True)
            yield cur_text
            # info_list.append(cur_text)
        elif item.name == 'dd':
            if first_text:
                for content in item:
                    if hasattr(content, 'get_text'):
                        cur_text = content.get_text()
                    else:
                        cur_text = content.strip()
                    if cur_text:
                        yield cur_text
                        break
            elif item.find_all('button'):
                btn_list = item.select('button.btn_sns02')
                sns_text_list = []
                for btn in btn_list:
                    script = btn.get('onclick')
                    link = re.search(r"open\('(.*?)'", script).group(1)
                    title = btn.get_text(strip=True)
                    sns_text_list.append(f'{title} ({link})')
                yield '\n'.join(sns_text_list)
            else:
                yield item.get_text(strip=True)


def get_dict_from_dl(dl, first_text=False):
    iter_dl = _dl_generator(dl, first_text)
    return dict(zip(iter_dl, iter_dl))