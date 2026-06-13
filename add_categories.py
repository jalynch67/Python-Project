from data import books
import pprint


category_map = {
    # J.R.R. Tolkien
    "The Hobbit": "Classic Fantasy",
    "The Fellowship of the Ring": "Epic Fantasy",
    "The Two Towers": "Epic Fantasy",
    "The Return of the King": "Epic Fantasy",
    "The Silmarillion": "Mythology",

    # George R.R. Martin
    "A Game of Thrones": "Grimdark Fantasy",
    "A Clash of Kings": "Grimdark Fantasy",
    "A Storm of Swords": "Grimdark Fantasy",
    "A Feast for Crows": "Grimdark Fantasy",
    "A Dance with Dragons": "Grimdark Fantasy",

    # Patrick Rothfuss
    "The Name of the Wind": "Coming-of-Age Fantasy",
    "The Wise Man's Fear": "Coming-of-Age Fantasy",

    # Brandon Sanderson - Stormlight
    "The Way of Kings": "Epic Fantasy",
    "Words of Radiance": "Epic Fantasy",
    "Oathbringer": "Epic Fantasy",
    "Rhythm of War": "Epic Fantasy",

    # Brandon Sanderson - Mistborn
    "Mistborn: The Final Empire": "Epic Fantasy",
    "The Well of Ascension": "Epic Fantasy",
    "The Hero of Ages": "Epic Fantasy",
    "The Alloy of Law": "Fantasy Western",
    "Shadows of Self": "Fantasy Western",
    "The Bands of Mourning": "Fantasy Western",

    # Brandon Sanderson - Standalones
    "Elantris": "Standalone Fantasy",
    "Warbreaker": "Standalone Fantasy",

    # Robert Jordan
    "The Eye of the World": "Epic Fantasy",
    "The Great Hunt": "Epic Fantasy",
    "The Dragon Reborn": "Epic Fantasy",
    "The Shadow Rising": "Epic Fantasy",
    "The Fires of Heaven": "Epic Fantasy",

    # J.K. Rowling
    "Harry Potter and the Philosopher's Stone": "Young Adult Fantasy",
    "Harry Potter and the Chamber of Secrets": "Young Adult Fantasy",
    "Harry Potter and the Prisoner of Azkaban": "Young Adult Fantasy",
    "Harry Potter and the Goblet of Fire": "Young Adult Fantasy",
    "Harry Potter and the Order of the Phoenix": "Young Adult Fantasy",
    "Harry Potter and the Half-Blood Prince": "Young Adult Fantasy",
    "Harry Potter and the Deathly Hallows": "Young Adult Fantasy",

    # C.S. Lewis
    "The Lion, the Witch and the Wardrobe": "Children's Fantasy",
    "Prince Caspian": "Children's Fantasy",
    "The Voyage of the Dawn Treader": "Children's Fantasy",
    "The Silver Chair": "Children's Fantasy",
    "The Magician's Nephew": "Children's Fantasy",
    "The Last Battle": "Children's Fantasy",

    # Neil Gaiman
    "American Gods": "Urban Fantasy",
    "Neverwhere": "Urban Fantasy",
    "Stardust": "Fairy Tale Fantasy",
    "The Ocean at the End of the Lane": "Literary Fantasy",

    # Terry Pratchett
    "The Colour of Magic": "Comic Fantasy",
    "Guards! Guards!": "Comic Fantasy",
    "Good Omens": "Comic Fantasy",
    "Small Gods": "Comic Fantasy",
    "Going Postal": "Comic Fantasy",

    # Robin Hobb
    "Assassin's Apprentice": "Character-Driven Fantasy",
    "Royal Assassin": "Character-Driven Fantasy",
    "Assassin's Quest": "Character-Driven Fantasy",

    # Joe Abercrombie
    "The Blade Itself": "Grimdark Fantasy",
    "Before They Are Hanged": "Grimdark Fantasy",
    "Last Argument of Kings": "Grimdark Fantasy",

    # Christopher Paolini
    "Eragon": "Dragon Fantasy",
    "Eldest": "Dragon Fantasy",
    "Brisingr": "Dragon Fantasy",
    "Inheritance": "Dragon Fantasy",

    # Scott Lynch
    "The Lies of Locke Lamora": "Adventure Fantasy",
    "Red Seas Under Red Skies": "Adventure Fantasy",
    "The Republic of Thieves": "Adventure Fantasy",

    # Sarah J. Maas
    "Throne of Glass": "Young Adult Fantasy",
    "Crown of Midnight": "Young Adult Fantasy",
    "A Court of Thorns and Roses": "Romantasy",
    "A Court of Mist and Fury": "Romantasy",
    "A Court of Wings and Ruin": "Romantasy",

    # Leigh Bardugo
    "Shadow and Bone": "Young Adult Fantasy",
    "Siege and Storm": "Young Adult Fantasy",
    "Ruin and Rising": "Young Adult Fantasy",
    "Six of Crows": "Heist Fantasy",
    "Crooked Kingdom": "Heist Fantasy",

    # Susanna Clarke
    "Jonathan Strange & Mr Norrell": "Historical Fantasy",
    "Piranesi": "Literary Fantasy",

    # Naomi Novik
    "Uprooted": "Fairy Tale Fantasy",
    "Spinning Silver": "Fairy Tale Fantasy",

    # Katherine Arden
    "The Bear and the Nightingale": "Historical Fantasy",
    "The Girl in the Tower": "Historical Fantasy",
    "The Winter of the Witch": "Historical Fantasy",

    # N.K. Jemisin
    "The Fifth Season": "Apocalyptic Fantasy",
    "The Obelisk Gate": "Apocalyptic Fantasy",
    "The Stone Sky": "Apocalyptic Fantasy",

    # R.F. Kuang
    "The Poppy War": "Dark Fantasy",
    "The Dragon Republic": "Dark Fantasy",
    "The Burning God": "Dark Fantasy",

    # Rebecca Yarros
    "Fourth Wing": "Romantasy",
    "Iron Flame": "Romantasy",

    # Classic / notable standalones
    "A Wizard of Earthsea": "Classic Fantasy",
    "The Tombs of Atuan": "Classic Fantasy",
    "The Farthest Shore": "Classic Fantasy",
    "The Once and Future King": "Arthurian Fantasy",
    "Legend": "Heroic Fantasy",
    "The Night Circus": "Magical Realism",
    "The Priory of the Orange Tree": "Epic Fantasy",
    "Magician": "Epic Fantasy",
    "Gardens of the Moon": "Epic Fantasy",
    "The Black Company": "Military Fantasy",
    "Tigana": "Historical Fantasy",
    "Prince of Thorns": "Grimdark Fantasy",
    "The Way of Shadows": "Assassin Fantasy",
}


for book in books:
    title = book.get("title")

    if title in category_map:
        book["category"] = category_map[title]
    else:
        book["category"] = "Fantasy"


with open("data.py", "w", encoding="utf-8") as file:
    file.write("books = ")
    file.write(pprint.pformat(books, width=120, sort_dicts=False))
    file.write("\n")

print("Done. Categories added to data.py")