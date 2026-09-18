import {
  ChevronLeft,
  ChevronRight,
  Pencil,
  Plus,
  Search,
  Trash2,
  UserCheck,
  UserX,
  Users,
} from "lucide-react";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  createSubscriber,
  deleteSubscriber,
  getSubscribers,
  updateSubscriber,
} from "../lib/api";

import {
  PageHeader,
} from "../components/PageHeader";

import {
  EmptyState,
} from "../components/EmptyState";

import {
  Spinner,
} from "../components/Spinner";

import {
  Modal,
} from "../components/Modal";

import type {
  Subscriber,
  SubscriberStatus,
} from "../types";


const PAGE_SIZE = 10;


export default function SubscribersPage() {
  const queryClient =
    useQueryClient();


  const [page, setPage] =
    useState(1);

  const [search, setSearch] =
    useState("");

  const [searchInput, setSearchInput] =
    useState("");

  const [statusFilter, setStatusFilter] =
    useState<
      "all" | SubscriberStatus
    >("all");


  const [modalOpen, setModalOpen] =
    useState(false);

  const [editing, setEditing] =
    useState<Subscriber | null>(
      null,
    );


  const [name, setName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [error, setError] =
    useState("");

  const [notice, setNotice] =
    useState("");


  useEffect(() => {
    const timeout =
      window.setTimeout(() => {
        setSearch(
          searchInput.trim(),
        );

        setPage(1);
      }, 350);

    return () =>
      window.clearTimeout(
        timeout,
      );
  }, [searchInput]);


  useEffect(() => {
    setPage(1);
  }, [statusFilter]);


  const subscribersQuery =
    useQuery({
      queryKey: [
        "subscribers",
        {
          page,
          page_size:
            PAGE_SIZE,
          search,
          status:
            statusFilter ===
            "all"
              ? undefined
              : statusFilter,
        },
      ],

      queryFn: () =>
        getSubscribers({
          page,
          page_size:
            PAGE_SIZE,
          search:
            search || undefined,
          status:
            statusFilter ===
            "all"
              ? undefined
              : statusFilter,
        }),
    });


  const createMutation =
    useMutation({
      mutationFn: () =>
        createSubscriber(
          name.trim(),
          email.trim(),
        ),

      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: [
            "subscribers",
          ],
        });

        closeModal();

        notify(
          "Subscriber added successfully.",
        );
      },

      onError: (err) => {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to add subscriber.",
        );
      },
    });


  const updateMutation =
    useMutation({
      mutationFn: () => {
        if (!editing) {
          throw new Error(
            "No subscriber selected.",
          );
        }

        return updateSubscriber(
          editing.id,
          {
            name: name.trim(),
            email: email.trim(),
          },
        );
      },

      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: [
            "subscribers",
          ],
        });

        closeModal();

        notify(
          "Subscriber updated successfully.",
        );
      },

      onError: (err) => {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to update subscriber.",
        );
      },
    });


  const deleteMutation =
    useMutation({
      mutationFn:
        deleteSubscriber,

      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: [
            "subscribers",
          ],
        });

        notify(
          "Subscriber deleted.",
        );
      },

      onError: (err) => {
        notify(
          err instanceof Error
            ? err.message
            : "Unable to delete subscriber.",
        );
      },
    });


  const statusMutation =
    useMutation({
      mutationFn: ({
        id,
        status,
      }: {
        id: number;
        status: SubscriberStatus;
      }) =>
        updateSubscriber(
          id,
          { status },
        ),

      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: [
            "subscribers",
          ],
        });
      },

      onError: (err) => {
        notify(
          err instanceof Error
            ? err.message
            : "Unable to change subscriber status.",
        );
      },
    });


  const data =
    subscribersQuery.data;


  function notify(
    message: string,
  ) {
    setNotice(message);

    window.setTimeout(
      () => setNotice(""),
      3000,
    );
  }


  function openCreate() {
    setEditing(null);
    setName("");
    setEmail("");
    setError("");
    setModalOpen(true);
  }


  function openEdit(
    subscriber: Subscriber,
  ) {
    setEditing(subscriber);
    setName(subscriber.name);
    setEmail(subscriber.email);
    setError("");
    setModalOpen(true);
  }


  function closeModal() {
    setModalOpen(false);
    setEditing(null);
    setName("");
    setEmail("");
    setError("");
  }


  function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    setError("");

    if (
      !name.trim() ||
      !email.trim()
    ) {
      setError(
        "Name and email are required.",
      );

      return;
    }

    if (editing) {
      updateMutation.mutate();
    } else {
      createMutation.mutate();
    }
  }


  function remove(
    subscriber: Subscriber,
  ) {
    if (
      window.confirm(
        `Delete ${subscriber.name}?`,
      )
    ) {
      deleteMutation.mutate(
        subscriber.id,
      );
    }
  }


  const totalPages =
    data?.total_pages ?? 0;


  return (
    <>
      <PageHeader
        eyebrow="Audience"
        title="Subscribers"
        description={
          data
            ? `${data.total} total subscribers`
            : "Manage your audience."
        }
        actions={
          <button
            type="button"
            className="button primary"
            onClick={openCreate}
          >
            <Plus size={16} />
            Add subscriber
          </button>
        }
      />


      {notice && (
        <div className="success-alert page-alert">
          {notice}
        </div>
      )}


      <div className="card">
        <div className="toolbar">
          <div className="search-box">
            <Search size={16} />

            <input
              value={
                searchInput
              }
              onChange={(event) =>
                setSearchInput(
                  event.target
                    .value,
                )
              }
              placeholder="Search name or email..."
              aria-label="Search subscribers"
            />
          </div>


          <div className="subscriber-toolbar-right">
            <select
              value={
                statusFilter
              }
              onChange={(event) =>
                setStatusFilter(
                  event.target
                    .value as
                    | "all"
                    | SubscriberStatus,
                )
              }
              aria-label="Filter subscribers by status"
            >
              <option value="all">
                All statuses
              </option>

              <option value="active">
                Active
              </option>

              <option value="inactive">
                Inactive
              </option>
            </select>


            <div className="toolbar-meta">
              <Users size={15} />

              {data?.total ??
                0}
            </div>
          </div>
        </div>


        {subscribersQuery.isLoading ? (
          <div className="center-loader">
            <Spinner size="medium" />
          </div>
        ) : subscribersQuery.isError ? (
          <div className="empty-state">
            <div className="empty-icon">
              <Users size={20} />
            </div>

            <h3>
              Unable to load subscribers
            </h3>

            <p>
              {
                subscribersQuery.error instanceof
                Error
                  ? subscribersQuery
                      .error.message
                  : "Please try again."
              }
            </p>
          </div>
        ) : !data ||
          data.items.length ===
            0 ? (
          <EmptyState
            title={
              search ||
              statusFilter !==
                "all"
                ? "No matching subscribers"
                : "No subscribers yet"
            }
            description={
              search ||
              statusFilter !==
                "all"
                ? "Try changing your search or filter."
                : "Start building your audience."
            }
            action={
              !search &&
              statusFilter ===
                "all" ? (
                <button
                  type="button"
                  className="button primary"
                  onClick={
                    openCreate
                  }
                >
                  <Plus size={16} />
                  Add subscriber
                </button>
              ) : undefined
            }
          />
        ) : (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>
                      Subscriber
                    </th>

                    <th>
                      Status
                    </th>

                    <th>
                      Added
                    </th>

                    <th />
                  </tr>
                </thead>

                <tbody>
                  {data.items.map(
                    (
                      subscriber,
                    ) => (
                      <tr
                        key={
                          subscriber.id
                        }
                      >
                        <td>
                          <div className="table-person">
                            <div className="person-avatar">
                              {subscriber.name
                                .charAt(
                                  0,
                                )
                                .toUpperCase()}
                            </div>

                            <div>
                              <strong>
                                {
                                  subscriber.name
                                }
                              </strong>

                              <span>
                                {
                                  subscriber.email
                                }
                              </span>
                            </div>
                          </div>
                        </td>


                        <td>
                          <button
                            type="button"
                            className={`status-badge status-button status-${subscriber.status}`}
                            onClick={() =>
                              statusMutation.mutate(
                                {
                                  id: subscriber.id,
                                  status:
                                    subscriber.status ===
                                    "active"
                                      ? "inactive"
                                      : "active",
                                },
                              )
                            }
                            disabled={
                              statusMutation.isPending
                            }
                          >
                            {subscriber.status ===
                            "active" ? (
                              <UserCheck
                                size={
                                  13
                                }
                              />
                            ) : (
                              <UserX
                                size={
                                  13
                                }
                              />
                            )}

                            {
                              subscriber.status
                            }
                          </button>
                        </td>


                        <td>
                          {new Date(
                            subscriber.created_at,
                          ).toLocaleDateString()}
                        </td>


                        <td>
                          <div className="row-actions">
                            <button
                              type="button"
                              className="icon-button"
                              onClick={() =>
                                openEdit(
                                  subscriber,
                                )
                              }
                              aria-label={`Edit ${subscriber.name}`}
                            >
                              <Pencil
                                size={
                                  15
                                }
                              />
                            </button>


                            <button
                              type="button"
                              className="icon-button danger"
                              onClick={() =>
                                remove(
                                  subscriber,
                                )
                              }
                              aria-label={`Delete ${subscriber.name}`}
                              disabled={
                                deleteMutation.isPending
                              }
                            >
                              <Trash2
                                size={
                                  15
                                }
                              />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>


            {totalPages > 1 && (
              <div className="pagination">
                <span>
                  Page {page} of{" "}
                  {totalPages}
                </span>

                <div className="pagination-actions">
                  <button
                    type="button"
                    className="icon-button"
                    disabled={
                      page <= 1 ||
                      subscribersQuery.isFetching
                    }
                    onClick={() =>
                      setPage(
                        (current) =>
                          Math.max(
                            1,
                            current -
                              1,
                          ),
                      )
                    }
                    aria-label="Previous page"
                  >
                    <ChevronLeft
                      size={16}
                    />
                  </button>

                  <button
                    type="button"
                    className="icon-button"
                    disabled={
                      page >=
                        totalPages ||
                      subscribersQuery.isFetching
                    }
                    onClick={() =>
                      setPage(
                        (current) =>
                          Math.min(
                            totalPages,
                            current +
                              1,
                          ),
                      )
                    }
                    aria-label="Next page"
                  >
                    <ChevronRight
                      size={16}
                    />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>


      <Modal
        open={modalOpen}
        title={
          editing
            ? "Edit subscriber"
            : "Add subscriber"
        }
        onClose={closeModal}
      >
        <form
          className="modal-form"
          onSubmit={submit}
        >
          {error && (
            <div className="form-error">
              {error}
            </div>
          )}

          <label>
            Name

            <input
              value={name}
              onChange={(event) =>
                setName(
                  event.target.value,
                )
              }
              placeholder="Subscriber name"
            />
          </label>


          <label>
            Email

            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value,
                )
              }
              placeholder="subscriber@example.com"
            />
          </label>


          <div className="modal-actions">
            <button
              type="button"
              className="button secondary"
              onClick={
                closeModal
              }
            >
              Cancel
            </button>

            <button
              type="submit"
              className="button primary"
              disabled={
                createMutation.isPending ||
                updateMutation.isPending
              }
            >
              {createMutation.isPending ||
              updateMutation.isPending
                ? "Saving..."
                : editing
                  ? "Save changes"
                  : "Add subscriber"}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}