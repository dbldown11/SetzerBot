import asqlite
import sqlite3

async def create_calmness_card() -> list:
    async with asqlite.connect(":memory:") as conn:
        conn.row_factory = sqlite3.Row
        card = (0, 'Special', 'Special', 4, 'Calmness', 'Remove a previously selected card from this seed', 0, None, 0,
        0)
        res = await conn.execute(
            "SELECT ? AS id, ? AS category, ? AS weighting, ? AS rarity, ? AS name, ? AS desc, ? AS difficulty, "
            "? AS mutual_exclusive, ? AS character, ? AS objectives",card)
        row = await res.fetchone()

    return row