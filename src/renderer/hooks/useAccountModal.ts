import { useCallback, useState } from "react";
import { Account } from "../../shared/types";
import { AccountActions } from "../designs/types";

/**
 * État + logique partagés de la modale d'ajout/édition de compte, factorisés
 * pour éviter la duplication entre les designs classic / modern / pro.
 */
export function useAccountModal(
  actions: Pick<AccountActions, "addAccount" | "updateAccount">,
) {
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<Account | null>(null);

  const openAdd = useCallback(() => {
    setEditing(null);
    setIsOpen(true);
  }, []);

  const openEdit = useCallback((account: Account) => {
    setEditing(account);
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    setEditing(null);
  }, []);

  const submit = useCallback(
    async (data: Partial<Account>) => {
      if (editing) {
        await actions.updateAccount({ ...editing, ...data } as Account);
      } else {
        await actions.addAccount(data);
      }
      setIsOpen(false);
      setEditing(null);
    },
    [editing, actions],
  );

  return { isOpen, editing, openAdd, openEdit, close, submit };
}
