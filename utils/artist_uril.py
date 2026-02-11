def getArtists(artists):
    artist_name = []
    for artist in artists:
        artist_name.append(artist['name'])
    artist_list = ','.join(artist_name)
    return artist_list
