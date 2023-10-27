from website import create_app


# create flask app
app = create_app()

# debug 
if __name__ == '__main__':
    app.run(debug=True)



# TODO:
# weights as ints
# formatting, display date/time w/ weight
# change home-> weight log
# admin@admin.com / admin