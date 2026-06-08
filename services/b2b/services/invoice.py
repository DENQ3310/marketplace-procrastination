from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from crud import invoice as invoice_crud
from crud import sku as sku_crud
from database.models.catalog.inventory import Invoice
from schemas.invoice import InvoiceCreate
from exceptions.invoice import InvoiceNotFoundError, InvalidInvoiceStatusError
from exceptions.sku import SkuNotFoundError


async def create_new_invoice(
	db: AsyncSession, invoice_data: InvoiceCreate, seller_id: UUID
) -> Invoice:
	for item in invoice_data.items:
		sku = await sku_crud.get_sku_by_id(db, item.sku_id)
		if not sku:
			raise SkuNotFoundError(f"SKU with id {item.sku_id} not found")

	return await invoice_crud.create_invoice(db, invoice_data, seller_id)


async def get_invoice(db: AsyncSession, invoice_id: UUID) -> Invoice | None:
	invoice = await invoice_crud.get_invoice_by_id(db, invoice_id)
	if not invoice:
		raise InvoiceNotFoundError()
	return invoice


async def accept_invoice(db: AsyncSession, invoice_id: UUID) -> Invoice:
	invoice = await invoice_crud.get_invoice_by_id(db, invoice_id)
	if not invoice:
		raise InvoiceNotFoundError(str(invoice_id))

	if invoice.status != "CREATED":
		raise InvalidInvoiceStatusError(invoice.status, "accept")

	for item in invoice.items:
		sku = await sku_crud.get_sku_by_id(db, item.sku_id)
		if sku:
			sku.active_quantity += item.quantity

	return await invoice_crud.update_invoice_to_accepted(db, invoice)


async def get_all_invoices(
	db: AsyncSession, skip: int = 0, limit: int = 10
) -> list[Invoice]:
	return await invoice_crud.get_all_invoices(db, skip=skip, limit=limit)


async def delete_invoice(db: AsyncSession, invoice_id: UUID) -> None:
	invoice = await invoice_crud.get_invoice_by_id(db, invoice_id)
	if not invoice:
		raise InvoiceNotFoundError(str(invoice_id))

	if invoice.status != "CREATED":
		raise InvalidInvoiceStatusError(invoice.status, "delete")

	await invoice_crud.delete_invoice(db, invoice)
