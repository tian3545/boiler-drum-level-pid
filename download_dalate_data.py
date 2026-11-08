#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import json, csv, time
import requests

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / 'data'
RAW_DIR = OUT_DIR / 'raw'
OUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

LAT, LON = '40.42', '110.03'
CITY = '达拉特旗'

ARCHIVE = 'https://archive-api.open-meteo.com/v1/archive'

HOURLY_VARS = ('temperature_2m,relative_humidity_2m,'
               'wind_speed_10m,surface_pressure')

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/141.0.0.0 Safari/537.36'
})

# 物理合理性检查范围
RANGE = {
    'temperature_2m': (-55.0, 55.0),       
    'relative_humidity_2m': (0.0, 100.0),  
    'wind_speed_10m': (0.0, 120.0),        
    'surface_pressure': (850.0, 1100.0),   
}
MAX_RETRY = 3


def fetch_archive():
    """抓取 2025 年全年逐小时历史气象，带重试。"""
    params = {
        'latitude': LAT, 'longitude': LON,
        'start_date': '2025-01-01', 'end_date': '2025-12-31',
        'hourly': HOURLY_VARS,
        'timezone': 'Asia/Shanghai',
    }
    for attempt in range(1, MAX_RETRY + 1):
        try:
            print(f'抓取 2025 年全年逐小时历史气象（UTC+8）...')
            resp = s.get(ARCHIVE, params=params, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            (RAW_DIR / 'archive_2025.json').write_text(
                json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
            return data
        except Exception as e:
            print(f'  第 {attempt}/{MAX_RETRY} 次请求失败：{e}')
            if attempt == MAX_RETRY:
                raise
            time.sleep(2 * attempt)
    raise RuntimeError('抓取失败')


def clean_rows(hourly):
    """按物理范围清洗逐小时数据，返回 (time, t, rh, ws, p) 行。"""
    times = hourly['time']
    cols = ['temperature_2m', 'relative_humidity_2m',
            'wind_speed_10m', 'surface_pressure']
    rows, dropped = [], 0
    for i, t in enumerate(times):
        vals = []
        ok = True
        for c in cols:
            try:
                v = float(hourly[c][i])
            except (TypeError, ValueError):
                v, ok = float('nan'), False
            lo, hi = RANGE[c]
            if not (lo <= v <= hi):
                ok = False
            vals.append(v)
        if not ok:
            dropped += 1
            continue
        rows.append((t, vals[0], vals[1], vals[2], vals[3]))
    return rows, dropped


def write_csv(path, header, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f'  已保存 {len(rows)} 行 -> {path.name}')


def main():
    print(f'== {CITY}（{LAT}N, {LON}E）气象数据采集 ==')
    arch = fetch_archive()

    rows, dropped = clean_rows(arch['hourly'])
    write_csv(OUT_DIR / 'dalate_weather_hourly.csv',
              ['time', 'temperature_2m_c', 'relative_humidity_2m_pct',
               'wind_speed_10m_kmh', 'surface_pressure_hpa'], rows)

    temps = [r[1] for r in rows]
    lines = [
        f'采集点：{CITY}（{LAT}N, {LON}E，海拔约 {arch.get("elevation", "?")} m）',
        f'数据源：Open-Meteo（archive API）',
        f'时间范围：{rows[0][0]} ~ {rows[-1][0]}（UTC+8）',
        f'逐小时记录：{len(rows)} 条（2025 年理论 8760 小时）',
        f'清洗剔除：{dropped} 条（超物理范围/缺值）',
        f'年平均气温：{sum(temps) / len(temps):.2f} °C',
        f'年最高气温：{max(temps):.2f} °C，年最低气温：{min(temps):.2f} °C',
        f'原始 JSON 留存：data/raw/',
    ]
    (OUT_DIR / 'summary.txt').write_text('\n'.join(lines), encoding='utf-8')
    print('\n'.join(lines))
    print('== 采集完成 ==')


if __name__ == '__main__':
    main()