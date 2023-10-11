from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)



# TODO:
# weights as ints
# formatting, display date/time w/ weight
# change home-> weight log