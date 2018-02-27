from django import template

register = template.Library()

@register.filter
def ellipsis_line(value, arg):
    # value로부터
    # arg에 주어진 line수만큼의
    # 문자열(Line)을 반환
    # 만약 arg의 line수보다
    # value의 line이 많으면
    # 마지막에 ...추가
    full_string = value
    full_string_split = [item for item in full_string.splitlines()]
    allowed_length = int(arg)
    processed_string_1 = full_string_split[:allowed_length]
    processed_string = '\n'.join(processed_string_1 + ['...'])

    return processed_string

# register.filter('ellipsis_line', ellipsis_line)