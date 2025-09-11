# AutoCull

Prototype for automatic photo culling software.

## Requirements

See `requirements.txt` for required dependencies.

Run `pip install -r requirements.txt` to install all

---

## Database

PostgreSQL - create db `autocull_db`

---

## Notes:

- Currently quite slow
- Need progress bars for UX
- Refactoring to be done for sidebar contents - exif, score, duplicates viewers. Too much code duplication
- Some classes can be broken down further
- Filmstrip viewer should use more of photoviewer for consistency TODO
- Collections management TODO
- Face detection TODO
- ML for photo scores TODO
- Histogram?
- Focus peaking
- Exif editor?
- Option to save photos to DB?
- RAW file handling TODO
- UI beautification
- Multi threading?

---
