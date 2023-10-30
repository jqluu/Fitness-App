from website import create_app


# create flask app
app = create_app()

# debug 
if __name__ == '__main__':
    app.run(debug=True)



# TODO:
# formatting, display date/time w/ weight
# weight graph in analytics
# curr/past date for weight

#db models
#new workout form




# admin@admin.com / admin