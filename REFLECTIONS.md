# Clean --apply blast radius: If you accidentally ran clean --tag Environment=dev --apply in an account shared with another team, what would you have wanted in place to limit damage?
If I accidentally ran `clean --apply` in an account shared with another team, I would have wanted the following things to limit damages:
- Confirm environment (development/ staging/ production)
- Summarize the number of resources before permanent deleting
- Implement protected tags for significant resources
- Implement IAM policy to prevent deleting production resources

# W7 carry-over: Which commands will you keep going into W7 (production-style multi-account)? Which would you drop and why?

I would like to keep the following commands into W7:
- `list`: this is core feature
- `cost`: this is cost tracking feature
- `tag`: this supports tagging governance
- `idle`: this is essential for cleanup

Generally, these commands are useful for resource management and observability

I am considering to drop `clean` since this is too risky for production platform if we use incorrectly or accidentally
