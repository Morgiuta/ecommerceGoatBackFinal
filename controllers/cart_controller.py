from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from config.database import get_db
from models.cart import CartModel, CartItemModel
from models.product import ProductModel
from schemas.cart_schema import CartResponse, CartItemBase

class CartController:
    def __init__(self):
        self.router = APIRouter(tags=["Cart"])
        self._register_routes()

    def _register_routes(self):
        
        # OBTENER CARRITO (Con validación automática de Stock)
        @self.router.get("/{client_id}", response_model=CartResponse)
        async def get_cart(client_id: int, db: Session = Depends(get_db)):
            # 1. Buscar o crear carrito
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if not cart:
                cart = CartModel(client_id=client_id)
                db.add(cart)
                db.commit()
                db.refresh(cart)
            
            # 2. SANITIZACIÓN: Verificar stock real de cada item
            has_adjustments = False
            items_to_remove = []
            
            # Preparamos la respuesta mapeando manualmente para inyectar mensajes
            response_items = []
            cart_total = 0.0

            for item in cart.items:
                if not item.product:
                    items_to_remove.append(item)
                    continue

                real_stock = item.product.stock
                adjustment_msg = None

                # Caso A: Producto se quedó sin stock (0) -> Lo marcamos para borrar o avisar
                if real_stock == 0:
                    item.quantity = 0 
                    # Opción: Borrarlo directamente o dejarlo en 0 con aviso.
                    # Vamos a dejarlo en 0 para que el usuario vea que se agotó.
                    adjustment_msg = "Producto agotado. Eliminado de la compra."
                    has_adjustments = True
                    # Si prefieres borrarlo de la BD descomenta:
                    # items_to_remove.append(item)

                # Caso B: Hay stock, pero menos del que el usuario pidió
                elif item.quantity > real_stock:
                    old_qty = item.quantity
                    item.quantity = real_stock # Ajustamos al máximo posible
                    adjustment_msg = f"Stock limitado. Cantidad ajustada de {old_qty} a {real_stock}."
                    has_adjustments = True
                    
                    # Guardamos el cambio en la BD inmediatamente
                    db.add(item) 

                # Calculamos subtotal solo con items validos (>0)
                if item.quantity > 0:
                    cart_total += item.quantity * item.product.price

                # Crear objeto de respuesta para este item
                item_resp = item.__dict__
                item_resp['product'] = item.product
                item_resp['adjustment_message'] = adjustment_msg
                response_items.append(item_resp)

            # Si hubo items para borrar (ej: productos eliminados de la BD)
            if items_to_remove:
                for i in items_to_remove:
                    db.delete(i)
                has_adjustments = True

            # Guardamos cualquier ajuste de cantidad en la base de datos
            if has_adjustments:
                db.commit()

            # 3. Construir respuesta final
            # Filtramos items con cantidad 0 para no mostrarlos en la lista de compra activa,
            # o los mostramos con alerta. En este caso los mostramos si tienen mensaje.
            final_items = [
                i for i in response_items 
                if i['quantity'] > 0 or i['adjustment_message']
            ]

            return {
                "id_key": cart.id_key,
                "client_id": cart.client_id,
                "items": final_items,
                "total": cart_total,
                "has_adjustments": has_adjustments
            }

        # AGREGAR (SUMAR) ITEM
        @self.router.post("/{client_id}/items")
        async def add_item(client_id: int, item_data: CartItemBase, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if not cart:
                cart = CartModel(client_id=client_id)
                db.add(cart)
                db.commit()
                db.refresh(cart)

            product = db.query(ProductModel).get(item_data.product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            
            existing_item = next((i for i in cart.items if i.product_id == item_data.product_id), None)
            
            if existing_item:
                new_qty = existing_item.quantity + item_data.quantity
                if new_qty > product.stock:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente. Máximo disponible: {product.stock}")
                existing_item.quantity = new_qty
            else:
                if item_data.quantity > product.stock:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente. Máximo disponible: {product.stock}")
                new_item = CartItemModel(cart_id=cart.id_key, product_id=item_data.product_id, quantity=item_data.quantity)
                db.add(new_item)
            
            db.commit()
            return {"message": "Item agregado"}

        # ACTUALIZAR CANTIDAD (PUT)
        @self.router.put("/{client_id}/items")
        async def update_item(client_id: int, item_data: CartItemBase, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if not cart: return {"message": "Carrito no encontrado"}

            item = next((i for i in cart.items if i.product_id == item_data.product_id), None)
            if not item:
                 raise HTTPException(status_code=404, detail="Item no encontrado")

            product = db.query(ProductModel).get(item_data.product_id)
            if item_data.quantity > product.stock:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente. Máximo disponible: {product.stock}")

            item.quantity = item_data.quantity
            db.commit()
            return {"message": "Cantidad actualizada"}

        # ELIMINAR ITEM
        @self.router.delete("/{client_id}/items/{product_id}")
        async def remove_item(client_id: int, product_id: int, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if not cart: return {"message": "Carrito no encontrado"}

            db.query(CartItemModel).filter(
                CartItemModel.cart_id == cart.id_key, 
                CartItemModel.product_id == product_id
            ).delete()
            db.commit()
            return {"message": "Item eliminado"}
            
        # VACIAR CARRITO
        @self.router.delete("/{client_id}")
        async def clear_cart(client_id: int, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if cart:
                db.query(CartItemModel).filter(CartItemModel.cart_id == cart.id_key).delete()
                db.commit()
            return {"message": "Carrito vaciado"}