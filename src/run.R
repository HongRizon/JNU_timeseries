.deck_run <- function(code) {
  # Runs one cell like the R console: echoes each line with "> " / "+ ",
  # prints visible values, prints warnings after each top-level call,
  # stops at the first error. Echo lines start with \001, a new plot page
  # writes a line "\002" (the page shows up in that place).
  fmt_call <- function(cl) {
    if (is.null(cl)) return(NULL)
    if (is.call(cl) && (identical(cl[[1L]], quote(eval)) ||
                        identical(cl[[1L]], quote(withVisible)))) return(NULL)
    d <- deparse(cl, nlines = 1L, width.cutoff = 60L)
    if (length(d) == 0L) NULL else d[1L]
  }
  say_cond <- function(head, cl, msg) {
    d <- fmt_call(cl)
    if (is.null(d)) {
      cat(head, ": ", msg, "\n", sep = "", file = stderr())
    } else if (nchar(d) + nchar(msg) > 66L) {
      cat(head, " in ", d, " : \n  ", msg, "\n", sep = "", file = stderr())
    } else {
      cat(head, " in ", d, " : ", msg, "\n", sep = "", file = stderr())
    }
  }
  say_warnings <- function(ws) {
    n <- length(ws)
    if (n == 0L) return(invisible())
    cat(if (n == 1L) "Warning message:\n" else "Warning messages:\n", file = stderr())
    for (k in seq_len(n)) {
      w <- ws[[k]]
      d <- fmt_call(conditionCall(w))
      msg <- conditionMessage(w)
      pre <- if (n == 1L) "" else paste0(k, ": ")
      if (is.null(d)) {
        cat(pre, msg, "\n", sep = "", file = stderr())
      } else if (nchar(d) + nchar(msg) > 66L) {
        cat(pre, "In ", d, " :\n  ", msg, "\n", sep = "", file = stderr())
      } else {
        cat(pre, "In ", d, " : ", msg, "\n", sep = "", file = stderr())
      }
    }
  }
  setHook("plot.new", function() {
    m <- par("mfg")
    if (m[1L] == 1L && m[2L] == 1L) cat("\002\n")
  }, "replace")
  on.exit(setHook("plot.new", NULL, "replace"), add = TRUE)

  lines <- strsplit(code, "\n", fixed = TRUE)[[1L]]
  exprs <- tryCatch(parse(text = code, keep.source = TRUE), error = function(e) e)
  if (inherits(exprs, "error")) {
    for (ln in lines) cat("\001", if (nzchar(trimws(ln))) "> " else "", ln, "\n", sep = "")
    cat("Error: ", conditionMessage(exprs), "\n", sep = "", file = stderr())
    return(invisible(FALSE))
  }
  srcrefs <- attr(exprs, "srcref")
  done <- 0L
  for (i in seq_along(exprs)) {
    sr <- srcrefs[[i]]
    first <- sr[1L]; last <- sr[3L]
    if (last > done) {
      for (k in seq.int(done + 1L, last)) {
        ln <- lines[k]
        if (k < first) {
          if (nzchar(trimws(ln))) cat("\001> ", ln, "\n", sep = "")
        } else {
          cat("\001", if (k == first) "> " else "+ ", ln, "\n", sep = "")
        }
      }
      done <- last
    }
    ws <- list()
    res <- withCallingHandlers(
      tryCatch({
        r <- withVisible(eval(exprs[[i]], envir = globalenv()))
        if (r$visible) print(r$value)
        NULL
      }, error = function(e) e),
      warning = function(w) {
        ws[[length(ws) + 1L]] <<- w
        invokeRestart("muffleWarning")
      })
    if (inherits(res, "error")) {
      say_cond("Error", conditionCall(res), conditionMessage(res))
      if (length(ws)) {
        cat("In addition: ", file = stderr())
        say_warnings(ws)
      }
      return(invisible(FALSE))
    }
    say_warnings(ws)
  }
  if (done < length(lines)) {
    for (k in seq.int(done + 1L, length(lines))) {
      if (nzchar(trimws(lines[k]))) cat("\001> ", lines[k], "\n", sep = "")
    }
  }
  invisible(TRUE)
}
