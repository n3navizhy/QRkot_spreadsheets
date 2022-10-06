from datetime import datetime
from typing import List

from aiogoogle import Aiogoogle

from app.constants import (G_COLUMN_COUNT, G_FORMAT, G_LOCALE, G_ROW_COUNT,
                           G_SHEET_ID, G_TITLE_CLOSE_SPEED, G_VERSION_DRIVE,
                           G_VERSION_SHEETS)
from app.core.config import settings


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(G_FORMAT)
    service = await wrapper_services.discover('sheets', G_VERSION_SHEETS)
    spreadsheets_body = {
        'properties': {'title': f'QRKot_Отчет на {now_date_time}',
                       'locale': G_LOCALE},
        'sheets': [{
            'properties': {'sheetType': 'GRID',
                           'sheetId': G_SHEET_ID,
                           'title': G_TITLE_CLOSE_SPEED,
                           'gridProperties': {'rowCount': G_ROW_COUNT,
                                              'columnCount': G_COLUMN_COUNT}
                           }
        }]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheets_body)
    )
    spreadsheetid = response['spreadsheetId']
    return spreadsheetid


async def set_user_permissions(
    spreadsheetid: str,
    wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email
    }
    service = await wrapper_services.discover('drive', G_VERSION_DRIVE)
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields='id'
        )
    )


async def spreadsheets_update_value(
    spreadsheetid: str,
    projects: List,
    wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(G_FORMAT)
    service = await wrapper_services.discover('sheets', G_VERSION_SHEETS)
    table_values = [
        ['Отчет от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    for project in projects:
        new_row = [
            str(project['name']),
            str(project['duration']),
            str(project['description'])
        ]
        table_values.append(new_row)
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    all_lines = len(table_values)
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range=f'A1:C{all_lines}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
