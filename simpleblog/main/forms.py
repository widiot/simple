from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import (ValidationError, StringField, SubmitField)
from wtforms.validators import (DataRequired, Length)


# 博客
class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(message='请填入标题')])
    body = PageDownField('内容', validators=[DataRequired(message='请写入博客')])
