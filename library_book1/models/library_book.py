
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

'''
创建图书、会员、借还记录、借书向导等4个实体的model，实现功能：从借书向导的表单获取会员和图书信息(使用self.member_id和self.book_ids)创建
借书记录（library.book.loan的record）
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
        self.state=new_state
    

class LibraryMember(models.Model):
    """ 
    只有一个基本字段member_number,表示会员卡
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

   The summary line for a class docstring should fit on one line.

    """

    _name = 'library.book.loan'
    _description = u'借还记录'
    _order = 'name ASC'

    name = fields.Char(string=u'Loan Reference',required=True,default=lambda self: _('New'))
    member_id = fields.Many2one(string=u'会员号',comodel_name='library.member',      required=True,) 
    book_id = fields.Many2one(string=u'图书',comodel_name='library.book',required=True,)  
    state = fields.Selection(string=u'状态',selection=[('ongoing', u'借出'), ('done', u'归还')])


class LibraryLoanWizard(models.TransientModel):
    """ 

   The summary line for a class docstring should fit on one line.

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
    
    


    

    
    
    




    




    


    

    


    

