
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

'''
创建图书、会员、借还记录、借书向导等4个实体的model，实现功能：从借书向导的表单获取会员和图书信息(使用self.member_id和self.book_ids),
执行record_borrows(books)方法，该方法调用会员对象的borrow_books(),创建借书记录（library.book.loan的record），loan的record的state默认为'ongoing',
borrow_books()方法又调用图书对象的change_state('borrowed')方法改变图书record对象的state字段为'外借'(borrowd)。
'''


class LibraryBook(models.Model):
    """ 
    基本字段图书名name和图书状态state，图书状态为available时，表示图书可以进行外借，状态为borrowed时，表示图书已外借，不可以再进行外借
    """

    _name = 'library.book'
    _description = u'图书'
    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(string=u'名称',required=True,)   
    state = fields.Selection(string=u'State',selection=[('available', 'Available'),('borrowed','Borrowed')])

    @api.multi
    def change_state(self,new_state):
        self.state=new_state  #self必须是singleton，不能是包含多个record的recordset
    

class LibraryMember(models.Model):
    """ 
    只有一个基本字段member_number,表示会员卡，borrow_books()方法创建loan实例，它的books参数是借书向导的record_borrows()方法调用它时传入的；
    borrow_books()又调用member.book的change_state()方法来改变图书的状态为"borrowed"。
    """
    
    _inherits = {'res.partner': 'partner_id'} 
    _name = 'library.member'
    _description = u'会员卡'

    member_number = fields.Char(string=u'卡号',required=True,)

    @api.multi
    def borrow_books(self,books):
        loan=self.env['library.book.loan']
        for book in books:
            vals=self._prepare_loan(book)
            loan.create(vals)
            book.change_state('borrowed')

    @api.multi
    def _prepare_loan(self,book):
        self.ensure_one()
        return {'book_id':book.id,'member_id':self.id}
        



class LibraryBookLoan(models.Model):
    """ 
    library.book.loan的state字段的默认值为ongoing，所以通过library.loan.wizard新创建的loan实例都是“借出”状态
    """

    _name = 'library.book.loan'
    _description = u'借还记录'
    _order = 'name ASC'

    name = fields.Char(string=u'Loan Reference',required=True,default=lambda self: _('New'))
    member_id = fields.Many2one(string=u'会员号',comodel_name='library.member',required=True,) 
    book_id = fields.Many2one(string=u'图书',comodel_name='library.book',required=True,)  
    state = fields.Selection(string=u'状态',selection=[('ongoing', u'借出'), ('done', u'归还')],default='ongoing',)


class LibraryLoanWizard(models.TransientModel):
    """ 
    通过library.loan.wizard的record_borrows()方法调用library.member的borrow_books(),并传入参数books（library.book的record）
    """

    _name = 'library.loan.wizard'
    _description = u'借书向导'
 
    member_id = fields.Many2one(string=u'会员',comodel_name='library.member',)
    book_ids = fields.Many2many(string=u'图书',comodel_name='library.book',domain="[('state','=','available')]",)

    @api.multi
    def record_borrows(self):
        self.ensure_one()
        books=self.book_ids
        member=self.member_id
        member.borrow_books(books)



class LibraryReturnWizard(models.TransientModel):
    """ 
    还书向导
    """

    _name = 'library.return.wizard'
    _description = u'还书向导'
    
    member_id = fields.Many2one(string=u'会员',comodel_name='library.member',ondelete='set null',)
    
    book_ids = fields.Many2many(string=u'图书',comodel_name='library.book',)
    
    @api.multi
    def record_returns(self):
        loan=self.env['library.book.loan']
        loans=loan.search([('book_id','in',self.book_ids.ids)]) #search()方法的参数是domain表达式，browse()的参数是id列表，它们都返回recordset
        for loan_rec in loans:
            loan_rec.write({'state':'done'})
        books=loans.mapped('book_id')
        books.change_state('available')


    

    


    

    


    

    
    
    




    




    


    

    


    

