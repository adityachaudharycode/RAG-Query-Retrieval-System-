# Gemini API Key Setup Guide

This guide will help you obtain the Gemini API key for the LLM-Powered Query-Retrieval System.

## 🔑 Required API Key

### Google Gemini API Key (for Embeddings & Text Generation)

**Step 1**: Visit Google AI Studio
- Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- Sign in with your Google account

**Step 2**: Create API Key
- Click "Create API Key"
- Select your Google Cloud project (or create a new one)
- Copy the generated API key

**Step 3**: Add to .env file
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## 💰 Cost Considerations

### Gemini API
- **Free Tier**: 15 requests per minute for Gemini 1.5 Flash
- **Embeddings**: $0.0001 per 1K characters for embedding-001
- **Text Generation**: $0.075 per 1M input tokens, $0.30 per 1M output tokens
- Very cost-effective for both embeddings and text generation

## 🔧 Configuration Options

### Use Sentence-Transformers Instead of Gemini (Free)

If you prefer not to use Gemini, you can use sentence-transformers (runs locally):

```env
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DIMENSION=384
```

### Alternative Gemini Models

You can use different Gemini models:

```env
GEMINI_MODEL=gemini-1.5-flash  # Fast and cost-effective (default)
# or
GEMINI_MODEL=gemini-1.5-pro    # Higher quality, more expensive
```

## 🚀 Quick Setup

1. Copy `.env.example` to `.env`
2. Add your Gemini API key to the `.env` file
3. Run `python run.py` to start the system

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and don't share them
- Consider using environment variables in production
- Monitor your API usage to avoid unexpected charges

## 🆘 Need Help?

- **Gemini API Issues**: Check [Google AI Studio Documentation](https://ai.google.dev/docs)
- **Billing Questions**: Check Google AI Studio billing section
- **Rate Limits**: Monitor your usage in Google AI Studio

---

**Ready to go?** Run `python run.py` to start the system!
