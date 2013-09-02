# Add your local node_modules bin to the path for this command
export PATH="./node_modules/.bin:$PATH"

# execute the rest of the command
exec "$@"
