export default async function handler(req, res) {
  try {
    const { tag, pagination_token } = req.query;
    if (!tag) {
      res.status(400).json({ message: "Missing required query param 'tag'" });
      return;
    }

    const apiKey = process.env.INSTAGRAM_API_KEY;
    if (!apiKey) {
      res.status(500).json({ message: 'Server misconfiguration: INSTAGRAM_API_KEY not set' });
      return;
    }

    const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
    const params = new URLSearchParams({ hashtag: String(tag) });
    if (pagination_token) params.set('pagination_token', String(pagination_token));

    const url = `${baseUrl}/search_hashtag.php?${params.toString()}`;

    const upstream = await fetch(url, {
      headers: {
        'X-RapidAPI-Key': apiKey,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
      },
      method: 'GET'
    });

    const text = await upstream.text();

    // Try to return JSON if possible; otherwise return text
    try {
      const data = JSON.parse(text);
      res.status(upstream.status).json(data);
    } catch (_) {
      res.status(upstream.status).send(text);
    }
  } catch (err) {
    res.status(500).json({ message: 'Unexpected server error', error: String(err) });
  }
}




